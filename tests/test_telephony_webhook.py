"""Integration tests for the /api/telephony/webhook/{provider} router.

Uses httpx.ASGITransport (the httpx>=0.26 replacement for the removed
AsyncClient(app=...) shortcut used elsewhere in this test suite).
"""

import base64
import hashlib
import hmac

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.main import app


def _twilio_signature(auth_token: str, url: str, params: dict) -> str:
    data = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))
    return base64.b64encode(
        hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")


@pytest.mark.asyncio
class TestTelephonyWebhookRouter:
    async def test_unknown_provider_returns_404(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/telephony/webhook/asterisk", data={})
            assert response.status_code == 404

    async def test_missing_signature_returns_403(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/telephony/webhook/twilio",
                data={"CallSid": "CA123", "CallStatus": "queued"},
            )
            assert response.status_code == 403

    async def test_valid_twilio_signature_returns_twiml(self, monkeypatch):
        get_settings.cache_clear()
        monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-token")
        get_settings.cache_clear()

        params = {"CallSid": "CA123", "From": "+15551234567", "To": "+15557654321", "CallStatus": "queued"}
        url = "http://test/api/telephony/webhook/twilio"
        signature = _twilio_signature("test-token", url, params)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/telephony/webhook/twilio",
                data=params,
                headers={"X-Twilio-Signature": signature},
            )

        get_settings.cache_clear()

        assert response.status_code == 200
        assert "<Say>" in response.text
