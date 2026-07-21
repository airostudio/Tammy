"""Tests for the Google Calendar and Microsoft Graph OAuth adapters.

All HTTP calls are mocked - there's no live Google/Microsoft account in
this environment. These verify the adapters build correct requests and
correctly interpret the documented response shapes, which is everything
that can be tested without a real OAuth app registered on each
provider's side.
"""

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app.calendar_sync.base import CalendarEvent
from app.calendar_sync.providers.google_calendar import GoogleCalendarProvider
from app.calendar_sync.providers.google_calendar import build_event_payload as google_payload
from app.calendar_sync.providers.microsoft_graph import MicrosoftGraphProvider
from app.calendar_sync.providers.microsoft_graph import build_event_payload as microsoft_payload
from app.calendar_sync.registry import get_calendar_provider
from app.config import Settings


def _event(**overrides):
    defaults = dict(
        id="evt1",
        title="Team sync",
        description=None,
        location=None,
        start_time=datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 1, 14, 30, tzinfo=timezone.utc),
        attendees=[],
    )
    defaults.update(overrides)
    return CalendarEvent(**defaults)


class TestGoogleCalendarProvider:
    def test_authorize_url_has_required_params(self):
        provider = GoogleCalendarProvider(Settings(google_client_id="abc123"))
        url = provider.get_authorize_url("state-xyz", "https://tammy.example.com/callback")

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        assert parsed.netloc == "accounts.google.com"
        assert params["client_id"] == ["abc123"]
        assert params["redirect_uri"] == ["https://tammy.example.com/callback"]
        assert params["access_type"] == ["offline"]
        assert params["prompt"] == ["consent"]
        assert params["state"] == ["state-xyz"]

    def test_event_payload_maps_fields(self):
        payload = google_payload(_event(location="Room 4", attendees=["Alice", "Bob"]))
        assert payload["summary"] == "Team sync"
        assert payload["location"] == "Room 4"
        assert "Attendees: Alice, Bob" in payload["description"]
        assert payload["start"]["dateTime"] == "2026-08-01T14:00:00+00:00"
        assert payload["end"]["dateTime"] == "2026-08-01T14:30:00+00:00"

    @pytest.mark.asyncio
    async def test_exchange_code_returns_oauth_token(self, monkeypatch):
        async def fake_post(self, url, data=None, **kwargs):
            assert url == "https://oauth2.googleapis.com/token"
            assert data["grant_type"] == "authorization_code"
            assert data["code"] == "the-code"
            return httpx.Response(200, json={
                "access_token": "access-1", "refresh_token": "refresh-1", "expires_in": 3600,
            }, request=httpx.Request("POST", url))

        async def fake_get(self, url, headers=None, **kwargs):
            assert "Bearer access-1" == headers["Authorization"]
            return httpx.Response(200, json={"email": "user@example.com"})

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
        monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

        provider = GoogleCalendarProvider(Settings(google_client_id="id", google_client_secret="secret"))
        token = await provider.exchange_code("the-code", "https://tammy.example.com/callback")

        assert token.access_token == "access-1"
        assert token.refresh_token == "refresh-1"
        assert token.account_email == "user@example.com"
        assert token.calendar_id == "primary"

    @pytest.mark.asyncio
    async def test_refresh_carries_forward_existing_refresh_token(self, monkeypatch):
        async def fake_post(self, url, data=None, **kwargs):
            assert data["grant_type"] == "refresh_token"
            return httpx.Response(
                200, json={"access_token": "access-2", "expires_in": 3600}, request=httpx.Request("POST", url)
            )

        async def fake_get(self, url, headers=None, **kwargs):
            return httpx.Response(200, json={"email": "user@example.com"})

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
        monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

        provider = GoogleCalendarProvider(Settings(google_client_id="id", google_client_secret="secret"))
        token = await provider.refresh_access_token("refresh-1")

        assert token.access_token == "access-2"
        assert token.refresh_token == "refresh-1"  # not re-issued by Google, carried forward

    @pytest.mark.asyncio
    async def test_push_event_returns_external_id(self, monkeypatch):
        async def fake_post(self, url, json=None, headers=None, **kwargs):
            assert url == "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            assert json["summary"] == "Team sync"
            assert headers["Authorization"] == "Bearer access-1"
            return httpx.Response(200, json={"id": "google-event-1"}, request=httpx.Request("POST", url))

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

        provider = GoogleCalendarProvider(Settings())
        external_id = await provider.push_event("access-1", "primary", _event())
        assert external_id == "google-event-1"

    @pytest.mark.asyncio
    async def test_delete_event_tolerates_already_deleted(self, monkeypatch):
        async def fake_delete(self, url, headers=None, **kwargs):
            return httpx.Response(404)

        monkeypatch.setattr(httpx.AsyncClient, "delete", fake_delete)

        provider = GoogleCalendarProvider(Settings())
        await provider.delete_event("access-1", "primary", "already-gone")  # should not raise


class TestMicrosoftGraphProvider:
    def test_authorize_url_has_required_params(self):
        provider = MicrosoftGraphProvider(Settings(microsoft_client_id="abc123"))
        url = provider.get_authorize_url("state-xyz", "https://tammy.example.com/callback")

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        assert parsed.netloc == "login.microsoftonline.com"
        assert params["client_id"] == ["abc123"]
        assert params["redirect_uri"] == ["https://tammy.example.com/callback"]
        assert params["state"] == ["state-xyz"]

    def test_event_payload_maps_fields(self):
        payload = microsoft_payload(_event(location="Room 4", attendees=["Alice"]))
        assert payload["subject"] == "Team sync"
        assert payload["location"]["displayName"] == "Room 4"
        assert "Attendees: Alice" in payload["body"]["content"]
        assert payload["start"]["timeZone"] == "UTC"
        assert payload["start"]["dateTime"] == "2026-08-01T14:00:00"

    @pytest.mark.asyncio
    async def test_exchange_code_returns_oauth_token(self, monkeypatch):
        async def fake_post(self, url, data=None, **kwargs):
            assert url == "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            assert data["grant_type"] == "authorization_code"
            return httpx.Response(200, json={
                "access_token": "access-1", "refresh_token": "refresh-1", "expires_in": 3600,
            }, request=httpx.Request("POST", url))

        async def fake_get(self, url, headers=None, **kwargs):
            assert url == "https://graph.microsoft.com/v1.0/me"
            return httpx.Response(200, json={"mail": "user@example.com"})

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
        monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

        provider = MicrosoftGraphProvider(Settings(microsoft_client_id="id", microsoft_client_secret="secret"))
        token = await provider.exchange_code("the-code", "https://tammy.example.com/callback")

        assert token.access_token == "access-1"
        assert token.account_email == "user@example.com"
        assert token.calendar_id is None

    @pytest.mark.asyncio
    async def test_push_event_uses_me_events_when_no_calendar_id(self, monkeypatch):
        async def fake_post(self, url, json=None, headers=None, **kwargs):
            assert url == "https://graph.microsoft.com/v1.0/me/events"
            return httpx.Response(200, json={"id": "ms-event-1"}, request=httpx.Request("POST", url))

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

        provider = MicrosoftGraphProvider(Settings())
        external_id = await provider.push_event("access-1", None, _event())
        assert external_id == "ms-event-1"

    @pytest.mark.asyncio
    async def test_delete_event_tolerates_already_deleted(self, monkeypatch):
        async def fake_delete(self, url, headers=None, **kwargs):
            return httpx.Response(404)

        monkeypatch.setattr(httpx.AsyncClient, "delete", fake_delete)

        provider = MicrosoftGraphProvider(Settings())
        await provider.delete_event("access-1", None, "already-gone")  # should not raise


class TestCalendarRegistry:
    def test_returns_google_provider(self):
        provider = get_calendar_provider("google", Settings())
        assert isinstance(provider, GoogleCalendarProvider)

    def test_returns_microsoft_provider(self):
        provider = get_calendar_provider("microsoft", Settings())
        assert isinstance(provider, MicrosoftGraphProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            get_calendar_provider("yahoo", Settings())
