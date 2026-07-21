"""Calendar integration endpoints.

/feed/{token}.ics is intentionally public (no admin session) - calendar
apps subscribe to a URL periodically, they can't do interactive cookie
login. It's gated instead by an unguessable token derived from
SECRET_KEY, not a real per-user secret, so anyone with the URL can read
appointments; treat it like a shared calendar link.

Google Calendar / Microsoft 365 OAuth connect endpoints live here too
once a provider is configured (see app/calendar_sync/providers/).
"""

import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.calendar_sync.ical_export import generate_ics_feed
from app.config import get_settings
from app.database import get_db
from app.services.appointment_service import AppointmentService
from app.utils.default_user import DEFAULT_USER_ID

router = APIRouter()


def _feed_token() -> str:
    settings = get_settings()
    return hmac.new(settings.secret_key.encode(), b"calendar-feed", hashlib.sha256).hexdigest()[:32]


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
