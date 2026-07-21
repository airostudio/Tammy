"""Microsoft 365/Outlook adapter - OAuth2 (Microsoft identity platform v2.0)
+ Microsoft Graph API.

Setup required before this can be used against a real account:
1. Register an app at https://portal.azure.com under
   Azure Active Directory -> App registrations. "Accounts in any
   organizational directory and personal Microsoft accounts" gives the
   broadest reach (matches the "common" tenant used below).
2. Under Certificates & secrets, create a client secret.
3. Under Authentication, add
   "<PUBLIC_BASE_URL>/api/calendar/oauth/microsoft/callback" as a
   Web redirect URI.
4. Under API permissions, add Microsoft Graph delegated permissions
   Calendars.ReadWrite and offline_access.
5. Set MICROSOFT_CLIENT_ID / MICROSOFT_CLIENT_SECRET in the environment.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.calendar_sync.base import CalendarEvent, CalendarProvider, OAuthToken

AUTHORIZE_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
SCOPES = "offline_access openid email Calendars.ReadWrite"


def _to_iso_naive(value: datetime) -> str:
    """Graph wants a naive local-format timestamp plus a separate IANA
    timeZone field, rather than an offset-suffixed ISO string."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat()


def build_event_payload(event: CalendarEvent) -> dict:
    """Pure mapping from our normalized CalendarEvent to a Graph event body.

    Attendee names go into the body rather than Graph's `attendees` field,
    since that field requires real email addresses and chat-parsed names
    are just free text, not verified addresses.
    """
    content = event.description or ""
    if event.attendees:
        prefix = "\n\n" if content else ""
        content = f"{content}{prefix}Attendees: {', '.join(event.attendees)}"

    payload = {
        "subject": event.title,
        "body": {"contentType": "text", "content": content},
        "start": {"dateTime": _to_iso_naive(event.start_time), "timeZone": "UTC"},
        "end": {"dateTime": _to_iso_naive(event.end_time), "timeZone": "UTC"},
    }
    if event.location:
        payload["location"] = {"displayName": event.location}
    return payload


class MicrosoftGraphProvider(CalendarProvider):
    name = "microsoft"

    def __init__(self, settings):
        self._client_id = settings.microsoft_client_id
        self._client_secret = settings.microsoft_client_secret

    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "response_mode": "query",
            "scope": SCOPES,
            "state": state,
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthToken:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "scope": SCOPES,
                },
            )
            response.raise_for_status()
            return await self._to_oauth_token(client, response.json())

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                    "scope": SCOPES,
                },
            )
            response.raise_for_status()
            data = response.json()
            data.setdefault("refresh_token", refresh_token)
            return await self._to_oauth_token(client, data)

    async def _to_oauth_token(self, client: httpx.AsyncClient, data: dict) -> OAuthToken:
        access_token = data["access_token"]
        expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))

        account_email = None
        try:
            me = await client.get(f"{GRAPH_API_BASE}/me", headers={"Authorization": f"Bearer {access_token}"})
            if me.status_code == 200:
                profile = me.json()
                account_email = profile.get("mail") or profile.get("userPrincipalName")
        except httpx.HTTPError:
            pass  # non-fatal - the connection still works without a display email

        return OAuthToken(
            access_token=access_token,
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            account_email=account_email,
            calendar_id=None,  # Graph addresses the default calendar via /me/events directly
        )

    def _events_path(self, calendar_id: Optional[str]) -> str:
        if calendar_id:
            return f"{GRAPH_API_BASE}/me/calendars/{calendar_id}/events"
        return f"{GRAPH_API_BASE}/me/events"

    async def push_event(self, access_token: str, calendar_id: Optional[str], event: CalendarEvent) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._events_path(calendar_id),
                json=build_event_payload(event),
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()["id"]

    async def update_event(
        self, access_token: str, calendar_id: Optional[str], external_event_id: str, event: CalendarEvent
    ) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(
                f"{self._events_path(calendar_id)}/{external_event_id}",
                json=build_event_payload(event),
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()

    async def delete_event(self, access_token: str, calendar_id: Optional[str], external_event_id: str) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(
                f"{self._events_path(calendar_id)}/{external_event_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code not in (200, 204, 404):
                response.raise_for_status()
