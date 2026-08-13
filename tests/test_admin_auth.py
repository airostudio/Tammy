"""Tests for app/api/deps.py's require_admin - both auth paths it accepts:
the legacy admin-password session cookie, and a Supabase Auth Bearer token
(used by the Next.js frontend)."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.config import get_settings
from app.main import app


def _supabase_token(secret: str, **overrides) -> str:
    payload = {
        "aud": "authenticated",
        "role": "authenticated",
        "sub": "11111111-1111-1111-1111-111111111111",
        "email": "owner@example.com",
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    payload.update(overrides)
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.mark.asyncio
class TestSupabaseJwtAuth:
    async def test_valid_supabase_token_grants_access(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-secret")
        get_settings.cache_clear()

        token = _supabase_token("test-supabase-secret")

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/appointments/", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 200

        get_settings.cache_clear()

    async def test_token_signed_with_wrong_secret_rejected(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-secret")
        get_settings.cache_clear()

        token = _supabase_token("a-different-secret")

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/appointments/", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 401

        get_settings.cache_clear()

    async def test_expired_token_rejected(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-secret")
        get_settings.cache_clear()

        token = _supabase_token(
            "test-supabase-secret",
            exp=int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        )

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/appointments/", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 401

        get_settings.cache_clear()

    async def test_wrong_audience_rejected(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-secret")
        get_settings.cache_clear()

        token = _supabase_token("test-supabase-secret", aud="not-authenticated")

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/appointments/", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 401

        get_settings.cache_clear()

    async def test_disabled_when_secret_not_configured(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
        get_settings.cache_clear()

        token = _supabase_token("whatever-secret-the-token-happens-to-use")

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/appointments/", headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 401

        get_settings.cache_clear()

    async def test_legacy_cookie_session_still_works_alongside_supabase(self, monkeypatch):
        """Both auth paths must keep working - the built-in admin dashboard
        (cookie-based) and the Next.js frontend (Supabase JWT) can coexist."""
        monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-supabase-secret")
        monkeypatch.setenv("ADMIN_PASSWORD", "test1234")
        get_settings.cache_clear()

        transport = ASGITransport(app=app)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                login = await client.post("/api/admin/login", json={"password": "test1234"})
                assert login.status_code == 200

                response = await client.get("/api/appointments/")
                assert response.status_code == 200

        get_settings.cache_clear()
