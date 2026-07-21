"""Google Calendar adapter - OAuth2 authorization code flow + Calendar API v3.

Setup required before this can be used against a real account:
1. Create a project at https://console.cloud.google.com and enable the
   Google Calendar API.
2. Configure the OAuth consent screen (External or Internal).
3. Create an OAuth 2.0 Client ID (Web application) under
   APIs & Services -> Credentials.
4. Add "<PUBLIC_BASE_URL>/api/calendar/oauth/google/callback" as an
   authorized redirect URI.
5. Set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in the environment.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.calendar_sync.base import CalendarEvent, CalendarProvider, OAuthToken

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"
SCOPES = "https://www.googleapis.com/auth/calendar.events openid email"


def _to_iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat()


def build_event_payload(event: CalendarEvent) -> dict:
    """Pure mapping from our normalized CalendarEvent to Google's event body.

    Attendee names go into the description rather than the API's
    `attendees` field, since that field requires real email addresses and
    chat-parsed names are just free text, not verified addresses.
    """
    description = event.description or ""
    if event.attendees:
        prefix = "\n\n" if description else ""
        description = f"{description}{prefix}Attendees: {', '.join(event.attendees)}"

    return {
        "summary": event.title,
        "description": description or None,
        "location": event.location,
        "start": {"dateTime": _to_iso_utc(event.start_time)},
        "end": {"dateTime": _to_iso_utc(event.end_time)},
    }


class GoogleCalendarProvider(CalendarProvider):
    name = "google"

    def __init__(self, settings):
        self._client_id = settings.google_client_id
        self._client_secret = settings.google_client_secret

    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPES,
            "access_type": "offline",
            "prompt": "consent",
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
                },
            )
            response.raise_for_status()
            data = response.json()
            # Google doesn't re-issue a refresh_token on a refresh request -
            # carry the existing one forward so the caller keeps it.
            data.setdefault("refresh_token", refresh_token)
            return await self._to_oauth_token(client, data)

    async def _to_oauth_token(self, client: httpx.AsyncClient, data: dict) -> OAuthToken:
        access_token = data["access_token"]
        expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))

        account_email = None
        try:
            userinfo = await client.get(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
            if userinfo.status_code == 200:
                account_email = userinfo.json().get("email")
        except httpx.HTTPError:
            pass  # non-fatal - the connection still works without a display email

        return OAuthToken(
            access_token=access_token,
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            account_email=account_email,
            calendar_id="primary",
        )

    async def push_event(self, access_token: str, calendar_id: Optional[str], event: CalendarEvent) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{CALENDAR_API_BASE}/calendars/{calendar_id or 'primary'}/events",
                json=build_event_payload(event),
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()["id"]

    async def update_event(
        self, access_token: str, calendar_id: Optional[str], external_event_id: str, event: CalendarEvent
    ) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(
                f"{CALENDAR_API_BASE}/calendars/{calendar_id or 'primary'}/events/{external_event_id}",
                json=build_event_payload(event),
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()

    async def delete_event(self, access_token: str, calendar_id: Optional[str], external_event_id: str) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(
                f"{CALENDAR_API_BASE}/calendars/{calendar_id or 'primary'}/events/{external_event_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code not in (200, 204, 404):
                response.raise_for_status()
