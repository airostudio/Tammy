"""Calendar integration endpoints.

/feed/{token}.ics is intentionally public (no admin session) - calendar
apps subscribe to a URL periodically, they can't do interactive cookie
login. It's gated instead by an unguessable token derived from
SECRET_KEY, not a real per-user secret, so anyone with the URL can read
appointments; treat it like a shared calendar link.

/oauth/{provider}/callback is also intentionally public - it's the
redirect target Google/Microsoft send the browser back to after
consent, so it can't carry our admin session cookie forward reliably
across that cross-site redirect. It's protected instead by the signed,
short-lived `state` value that only this server could have issued.
"""

import hashlib
import hmac
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.calendar_sync.ical_export import generate_ics_feed
from app.calendar_sync.registry import get_calendar_provider
from app.calendar_sync.sync import save_calendar_connection
from app.config import get_settings
from app.database import get_db
from app.models.calendar_connection import CalendarConnection
from app.services.appointment_service import AppointmentService
from app.utils.auth import create_access_token, decode_access_token
from app.utils.default_user import DEFAULT_USER_ID

router = APIRouter()


def _feed_token() -> str:
    settings = get_settings()
    return hmac.new(settings.secret_key.encode(), b"calendar-feed", hashlib.sha256).hexdigest()[:32]


def _redirect_uri(request: Request, provider_name: str) -> str:
    settings = get_settings()
    base = (settings.public_base_url or str(request.base_url)).rstrip("/")
    return f"{base}/api/calendar/oauth/{provider_name}/callback"


@router.get("/feed/{token}.ics")
async def calendar_feed(token: str, db: AsyncSession = Depends(get_db)):
    """Public, token-gated .ics feed - subscribe to this URL from any calendar app"""
    if not hmac.compare_digest(token, _feed_token()):
        raise HTTPException(status_code=404, detail="Not found")

    appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID)
    ics_content = generate_ics_feed(appointments)
    return Response(content=ics_content, media_type="text/calendar; charset=utf-8")


@router.get("/feed-url")
async def get_feed_url(_admin: dict = Depends(require_admin)):
    """Admin-only: the path to subscribe to (prefix with your domain)"""
    return {"path": f"/api/calendar/feed/{_feed_token()}.ics"}


@router.get("/connections")
async def list_connections(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_admin)):
    """Admin-only: which calendars are connected right now"""
    result = await db.execute(select(CalendarConnection).where(CalendarConnection.user_id == DEFAULT_USER_ID))
    connections = result.scalars().all()
    return [
        {
            "provider": c.provider,
            "account_email": c.external_account_email,
            "connected_at": c.created_at,
        }
        for c in connections
    ]


@router.delete("/connections/{provider_name}")
async def disconnect_calendar(
    provider_name: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_admin)
):
    """Admin-only: disconnect a calendar (does not affect already-pushed events)"""
    result = await db.execute(
        select(CalendarConnection).where(
            CalendarConnection.user_id == DEFAULT_USER_ID, CalendarConnection.provider == provider_name
        )
    )
    connection = result.scalar_one_or_none()
    if connection:
        await db.delete(connection)
        await db.commit()
    return {"status": "ok"}


@router.get("/oauth/{provider_name}/connect")
async def start_oauth_connect(provider_name: str, request: Request, _admin: dict = Depends(require_admin)):
    """Admin-only: sends the caller to the provider's consent screen.

    Redirects by default, so a plain <a href> works from the
    cookie-authenticated public/admin/ dashboard (same origin as this
    API). Returns JSON instead when the caller sends
    Accept: application/json - used by the Next.js frontend, which
    authenticates with a Bearer token that a plain browser navigation
    can't carry cross-origin, so it fetches this URL instead and
    performs the redirect itself client-side.
    """
    settings = get_settings()
    try:
        provider = get_calendar_provider(provider_name, settings)
    except ValueError:
        raise HTTPException(status_code=404, detail="Unknown calendar provider")

    state = create_access_token({"provider": provider_name}, expires_delta=timedelta(minutes=10))
    authorize_url = provider.get_authorize_url(state, _redirect_uri(request, provider_name))

    if request.headers.get("accept", "").startswith("application/json"):
        return {"authorize_url": authorize_url}
    return RedirectResponse(authorize_url)


@router.get("/oauth/{provider_name}/callback")
async def oauth_callback(
    provider_name: str, code: str, state: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Public - see module docstring for why. Exchanges the code, stores
    the connection, and sends the browser back to the admin dashboard."""
    payload = decode_access_token(state)
    if not payload or payload.get("provider") != provider_name:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    settings = get_settings()
    try:
        provider = get_calendar_provider(provider_name, settings)
    except ValueError:
        raise HTTPException(status_code=404, detail="Unknown calendar provider")

    token = await provider.exchange_code(code, _redirect_uri(request, provider_name))
    await save_calendar_connection(db, DEFAULT_USER_ID, provider_name, token)

    settings = get_settings()
    if settings.frontend_url:
        return RedirectResponse(f"{settings.frontend_url.rstrip('/')}/admin/calendar")
    return RedirectResponse("/admin#calendar")
