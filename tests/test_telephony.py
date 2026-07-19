"""Tests for the carrier-agnostic telephony abstraction.

Covers signature verification and event parsing for each adapter in
isolation (no network calls), plus the registry and webhook router
wiring. TelnyxProvider.execute_actions is monkeypatched to avoid making
real HTTPS calls out to Telnyx's API during tests.
"""

import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx
import pytest
from nacl.signing import SigningKey

from app.config import Settings
from app.telephony.call_handler import CallEventHandler
from app.telephony.models import Answer, CallDirection, CallEventType, Speak
from app.telephony.providers.telnyx_provider import TelnyxProvider
from app.telephony.providers.twilio_provider import TwilioProvider
from app.telephony.registry import get_telephony_provider


# --- Twilio ---------------------------------------------------------------


class TestTwilioProvider:
    def _signed_request(self, auth_token: str, url: str, params: dict):
        body = urlencode(params).encode("utf-8")
        data = url + "".join(f"{k}{v}" for k, v in sorted(params.items()))
        signature = base64.b64encode(
            hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
        ).decode("utf-8")
        return body, signature

    def test_verify_signature_accepts_valid_request(self):
        provider = TwilioProvider(Settings(twilio_auth_token="test-token"))
        url = "https://tammy.example.com/api/telephony/webhook/twilio"
        params = {"CallSid": "CA123", "From": "+15551234567", "To": "+15557654321", "CallStatus": "ringing"}
        body, signature = self._signed_request("test-token", url, params)

        assert provider.verify_signature({"x-twilio-signature": signature}, body, url) is True

    def test_verify_signature_rejects_tampered_body(self):
        provider = TwilioProvider(Settings(twilio_auth_token="test-token"))
        url = "https://tammy.example.com/api/telephony/webhook/twilio"
        params = {"CallSid": "CA123", "From": "+15551234567", "To": "+15557654321", "CallStatus": "ringing"}
        body, signature = self._signed_request("test-token", url, params)

        tampered_body = body.replace(b"CA123", b"CA999")
        assert provider.verify_signature({"x-twilio-signature": signature}, tampered_body, url) is False

    def test_verify_signature_rejects_missing_signature(self):
        provider = TwilioProvider(Settings(twilio_auth_token="test-token"))
        assert provider.verify_signature({}, b"CallSid=CA123", "https://tammy.example.com/x") is False

    def test_parse_event_initiated_call(self):
        provider = TwilioProvider(Settings())
        body = b"CallSid=CA123&From=%2B15551234567&To=%2B15557654321&CallStatus=queued&Direction=inbound"
        event = provider.parse_event({}, body)

        assert event.provider == "twilio"
        assert event.event_type == CallEventType.INITIATED
        assert event.call_id == "CA123"
        assert event.from_number == "+15551234567"
        assert event.direction == CallDirection.INBOUND

    def test_parse_event_dtmf(self):
        provider = TwilioProvider(Settings())
        body = b"CallSid=CA123&From=%2B15551234567&To=%2B15557654321&Digits=42"
        event = provider.parse_event({}, body)
        assert event.event_type == CallEventType.DTMF
        assert event.dtmf_digits == "42"

    @pytest.mark.asyncio
    async def test_execute_actions_builds_twiml(self):
        provider = TwilioProvider(Settings())
        event = provider.parse_event({}, b"CallSid=CA123&From=%2B1&To=%2B2&CallStatus=queued")
        response = await provider.execute_actions(event, [Answer(), Speak(text="Hello there")])

        assert response.media_type == "application/xml"
        body = response.body.decode("utf-8")
        assert "<Say>Hello there</Say>" in body
        assert "<Response>" in body


# --- Telnyx -----------------------------------------------------------------


class TestTelnyxProvider:
    def _keypair(self):
        signing_key = SigningKey.generate()
        public_key_b64 = base64.b64encode(bytes(signing_key.verify_key)).decode("utf-8")
        return signing_key, public_key_b64

    def _signed_request(self, signing_key: SigningKey, body: bytes, timestamp: str):
        message = f"{timestamp}|{body.decode('utf-8')}".encode("utf-8")
        signature = base64.b64encode(signing_key.sign(message).signature).decode("utf-8")
        return signature

    def test_verify_signature_accepts_valid_request(self):
        signing_key, public_key_b64 = self._keypair()
        provider = TelnyxProvider(Settings(telnyx_public_key=public_key_b64))
        body = b'{"data": {"event_type": "call.initiated"}}'
        timestamp = str(int(time.time()))
        signature = self._signed_request(signing_key, body, timestamp)

        headers = {"telnyx-signature-ed25519": signature, "telnyx-timestamp": timestamp}
        assert provider.verify_signature(headers, body, "https://tammy.example.com/x") is True

    def test_verify_signature_rejects_tampered_body(self):
        signing_key, public_key_b64 = self._keypair()
        provider = TelnyxProvider(Settings(telnyx_public_key=public_key_b64))
        body = b'{"data": {"event_type": "call.initiated"}}'
        timestamp = str(int(time.time()))
        signature = self._signed_request(signing_key, body, timestamp)

        headers = {"telnyx-signature-ed25519": signature, "telnyx-timestamp": timestamp}
        tampered_body = b'{"data": {"event_type": "call.hangup"}}'
        assert provider.verify_signature(headers, tampered_body, "https://tammy.example.com/x") is False

    def test_verify_signature_rejects_stale_timestamp(self):
        signing_key, public_key_b64 = self._keypair()
        provider = TelnyxProvider(Settings(telnyx_public_key=public_key_b64))
        body = b'{"data": {"event_type": "call.initiated"}}'
        stale_timestamp = str(int(time.time()) - 3600)
        signature = self._signed_request(signing_key, body, stale_timestamp)

        headers = {"telnyx-signature-ed25519": signature, "telnyx-timestamp": stale_timestamp}
        assert provider.verify_signature(headers, body, "https://tammy.example.com/x") is False

    def test_parse_event_answered_call(self):
        provider = TelnyxProvider(Settings())
        body = (
            b'{"data": {"event_type": "call.answered", "payload": '
            b'{"call_control_id": "v3:abc", "from": "+15551234567", "to": "+15557654321", '
            b'"direction": "incoming"}}}'
        )
        event = provider.parse_event({}, body)

        assert event.provider == "telnyx"
        assert event.event_type == CallEventType.ANSWERED
        assert event.call_id == "v3:abc"
        assert event.direction == CallDirection.INBOUND

    @pytest.mark.asyncio
    async def test_execute_actions_sends_call_control_commands(self, monkeypatch):
        provider = TelnyxProvider(Settings(telnyx_api_key="test-key"))
        event = provider.parse_event(
            {},
            b'{"data": {"event_type": "call.initiated", "payload": {"call_control_id": "v3:abc"}}}',
        )

        sent_paths = []

        async def fake_post(self, path, json=None):
            sent_paths.append(path)
            return httpx.Response(200, json={"data": {}})

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

        result = await provider.execute_actions(event, [Answer(), Speak(text="Hi")])

        assert result is None  # command-driven: nothing to return to the webhook caller
        assert sent_paths == ["/calls/v3:abc/actions/answer", "/calls/v3:abc/actions/speak"]


# --- Registry -----------------------------------------------------------------


class TestRegistry:
    def test_returns_twilio_provider(self):
        provider = get_telephony_provider("twilio", Settings())
        assert isinstance(provider, TwilioProvider)

    def test_returns_telnyx_provider(self):
        provider = get_telephony_provider("telnyx", Settings())
        assert isinstance(provider, TelnyxProvider)

    def test_defaults_to_settings_value(self):
        provider = get_telephony_provider(settings=Settings(telephony_provider="twilio"))
        assert isinstance(provider, TwilioProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError):
            get_telephony_provider("asterisk", Settings())


# --- Call handler (business logic, provider-agnostic) ------------------------


class TestCallEventHandler:
    @pytest.mark.asyncio
    async def test_initiated_call_is_answered_and_greeted(self):
        handler = CallEventHandler()
        provider = TwilioProvider(Settings())
        event = provider.parse_event({}, b"CallSid=CA1&From=%2B1&To=%2B2&CallStatus=queued")

        actions = await handler.handle_event(event)

        assert any(isinstance(a, Answer) for a in actions)
        assert any(isinstance(a, Speak) for a in actions)
