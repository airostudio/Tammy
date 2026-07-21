"""Tests for calendar sync: the iCal export format, the feed endpoint,
and the idempotent column-upgrade helper that retrofits new columns onto
tables that already exist in a live database."""

from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.calendar_sync.ical_export import generate_ics_feed
from app.database import Base, _add_missing_columns
from app.main import app


def _fake_appointment(**overrides):
    defaults = dict(
        id="abc123",
        title="Team sync",
        description=None,
        location=None,
        start_time=datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 1, 14, 30, tzinfo=timezone.utc),
        status="scheduled",
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestIcsExport:
    def test_generates_valid_vcalendar_structure(self):
        ics = generate_ics_feed([_fake_appointment()])
        assert ics.startswith("BEGIN:VCALENDAR\r\n")
        assert ics.endswith("END:VCALENDAR\r\n")
        assert "BEGIN:VEVENT" in ics
        assert "END:VEVENT" in ics
        assert "SUMMARY:Team sync" in ics
        assert "DTSTART:20260801T140000Z" in ics
        assert "DTEND:20260801T143000Z" in ics
        assert "UID:abc123@tammy" in ics

    def test_cancelled_appointment_marked_cancelled(self):
        ics = generate_ics_feed([_fake_appointment(status="cancelled")])
        assert "STATUS:CANCELLED" in ics

    def test_special_characters_are_escaped(self):
        ics = generate_ics_feed([_fake_appointment(title="Q3 Review; Planning, Notes\nmore")])
        assert "SUMMARY:Q3 Review\\; Planning\\, Notes\\nmore" in ics

    def test_empty_list_still_valid_calendar(self):
        ics = generate_ics_feed([])
        assert "BEGIN:VCALENDAR" in ics
        assert "END:VCALENDAR" in ics
        assert "BEGIN:VEVENT" not in ics


class TestColumnUpgrade:
    @pytest.mark.asyncio
    async def test_adds_missing_column_to_existing_table(self):
        """Simulate a database that already has an "old" appointments table
        (created before external_calendar_provider/event_id existed) and
        confirm the upgrade helper adds them without erroring."""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with engine.begin() as conn:
                # Minimal "old" table - missing the two new columns entirely
                await conn.execute(text(
                    "CREATE TABLE appointments (id VARCHAR PRIMARY KEY, title VARCHAR)"
                ))

            async with engine.begin() as conn:
                await conn.run_sync(_add_missing_columns)

            async with engine.begin() as conn:
                def _get_columns(sync_conn):
                    return {c["name"] for c in inspect(sync_conn).get_columns("appointments")}
                columns = await conn.run_sync(_get_columns)

            assert "external_calendar_provider" in columns
            assert "external_calendar_event_id" in columns
        finally:
            await engine.dispose()

    @pytest.mark.asyncio
    async def test_running_twice_is_a_no_op(self):
        """The upgrade must be safe to run on every startup, not just once"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.run_sync(_add_missing_columns)
                await conn.run_sync(_add_missing_columns)  # should not raise
        finally:
            await engine.dispose()


@pytest.mark.asyncio
class TestCalendarFeedEndpoint:
    async def test_feed_url_requires_admin_session(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        from app.config import get_settings
        get_settings.cache_clear()

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/calendar/feed-url")
                assert response.status_code == 401

        get_settings.cache_clear()

    async def test_feed_is_public_but_token_gated(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        from app.config import get_settings
        get_settings.cache_clear()

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                await client.post("/api/chat/", json={"message": "Schedule a meeting with John tomorrow at 2pm"})

                login = await client.post("/api/admin/login", json={"password": "test1234"})
                assert login.status_code == 200

                feed_url_response = await client.get("/api/calendar/feed-url")
                assert feed_url_response.status_code == 200
                feed_path = feed_url_response.json()["path"]

            # A separate, unauthenticated client - no cookie at all
            async with AsyncClient(transport=transport, base_url="http://test") as anon_client:
                feed_response = await anon_client.get(feed_path)
                assert feed_response.status_code == 200
                assert "text/calendar" in feed_response.headers["content-type"]
                assert "Meeting with John" in feed_response.text

                wrong_token = await anon_client.get("/api/calendar/feed/not-the-real-token.ics")
                assert wrong_token.status_code == 404

        get_settings.cache_clear()


@pytest.mark.asyncio
class TestCalendarOAuthFlow:
    """End-to-end connect -> callback -> list -> disconnect, with Google's
    real endpoints faked. Only httpx calls to Google's own domains are
    intercepted - the test client's calls to our own app (also made via
    httpx.AsyncClient, over the ASGI transport) must pass through
    untouched, or the test would be faking its own requests to itself."""

    async def test_full_connect_and_disconnect_flow(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("PUBLIC_BASE_URL", "https://tammy.example.com")
        from app.config import get_settings
        get_settings.cache_clear()

        original_post = httpx.AsyncClient.post
        original_get = httpx.AsyncClient.get

        async def dispatching_post(self, url, *args, **kwargs):
            if isinstance(url, str) and "oauth2.googleapis.com" in url:
                return httpx.Response(
                    200,
                    json={"access_token": "fake-access", "refresh_token": "fake-refresh", "expires_in": 3600},
                    request=httpx.Request("POST", url),
                )
            return await original_post(self, url, *args, **kwargs)

        async def dispatching_get(self, url, *args, **kwargs):
            if isinstance(url, str) and "openidconnect.googleapis.com" in url:
                return httpx.Response(200, json={"email": "owner@example.com"})
            return await original_get(self, url, *args, **kwargs)

        monkeypatch.setattr(httpx.AsyncClient, "post", dispatching_post)
        monkeypatch.setattr(httpx.AsyncClient, "get", dispatching_get)

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                login = await client.post("/api/admin/login", json={"password": "test1234"})
                assert login.status_code == 200

                connect = await client.get("/api/calendar/oauth/google/connect", follow_redirects=False)
                assert connect.status_code in (302, 307)
                authorize_url = connect.headers["location"]
                assert authorize_url.startswith("https://accounts.google.com")
                state = parse_qs(urlparse(authorize_url).query)["state"][0]

                callback = await client.get(
                    f"/api/calendar/oauth/google/callback?code=fake-code&state={state}",
                    follow_redirects=False,
                )
                assert callback.status_code in (302, 307)

                connections = await client.get("/api/calendar/connections")
                assert connections.status_code == 200
                data = connections.json()
                assert len(data) == 1
                assert data[0]["provider"] == "google"
                assert data[0]["account_email"] == "owner@example.com"

                disconnect = await client.delete("/api/calendar/connections/google")
                assert disconnect.status_code == 200

                connections_after = await client.get("/api/calendar/connections")
                assert connections_after.json() == []

        get_settings.cache_clear()

    async def test_callback_rejects_forged_state(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
        from app.config import get_settings
        get_settings.cache_clear()

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/calendar/oauth/google/callback?code=fake-code&state=not-a-real-token",
                    follow_redirects=False,
                )
                assert response.status_code == 400

        get_settings.cache_clear()

    async def test_connect_requires_admin_session(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        from app.config import get_settings
        get_settings.cache_clear()

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/calendar/oauth/google/connect", follow_redirects=False)
                assert response.status_code == 401

        get_settings.cache_clear()
