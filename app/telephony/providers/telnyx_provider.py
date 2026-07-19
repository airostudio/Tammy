"""Telnyx adapter - command-driven call control via the Call Control REST API.

Signature verification follows Telnyx's documented Ed25519 scheme
(https://developers.telnyx.com/docs/api/v2/overview/Webhooks#verifying-webhooks),
including the recommended timestamp tolerance to reject replayed webhooks.
"""

import base64
import json
import time
from typing import Dict, List, Optional

import httpx
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from starlette.responses import Response

from app.telephony.base import TelephonyProvider
from app.telephony.models import (
    Answer,
    CallAction,
    CallDirection,
    CallEvent,
    CallEventType,
    Dial,
    Gather,
    Hangup,
    Reject,
    Speak,
    StartStream,
)

_EVENT_TYPE_MAP = {
    "call.initiated": CallEventType.INITIATED,
    "call.ringing": CallEventType.RINGING,
    "call.answered": CallEventType.ANSWERED,
    "call.hangup": CallEventType.HANGUP,
    "call.dtmf.received": CallEventType.DTMF,
    "call.gather.ended": CallEventType.SPEECH,
}

_SIGNATURE_TOLERANCE_SECONDS = 300


class TelnyxProvider(TelephonyProvider):
    name = "telnyx"

    def __init__(self, settings):
        self._public_key = settings.telnyx_public_key
        self._api_key = settings.telnyx_api_key
        self._api_base = "https://api.telnyx.com/v2"

    def verify_signature(self, headers: Dict[str, str], raw_body: bytes, url: str) -> bool:
        signature = headers.get("telnyx-signature-ed25519")
        timestamp = headers.get("telnyx-timestamp")
        if not signature or not timestamp or not self._public_key:
            return False
        try:
            if abs(time.time() - int(timestamp)) > _SIGNATURE_TOLERANCE_SECONDS:
                return False
            verify_key = VerifyKey(base64.b64decode(self._public_key))
            message = f"{timestamp}|{raw_body.decode('utf-8')}".encode("utf-8")
            verify_key.verify(message, base64.b64decode(signature))
            return True
        except (BadSignatureError, ValueError):
            return False

    def parse_event(self, headers: Dict[str, str], raw_body: bytes) -> CallEvent:
        body = json.loads(raw_body)
        data = body.get("data", {})
        payload = data.get("payload", {})
        event_type = _EVENT_TYPE_MAP.get(data.get("event_type", ""), CallEventType.UNKNOWN)

        direction = (
            CallDirection.INBOUND if payload.get("direction") == "incoming" else CallDirection.OUTBOUND
        )

        return CallEvent(
            provider=self.name,
            event_type=event_type,
            call_id=payload.get("call_control_id", ""),
            from_number=payload.get("from", ""),
            to_number=payload.get("to", ""),
            direction=direction,
            dtmf_digits=payload.get("digit"),
            speech_result=(
                payload.get("result") if data.get("event_type") == "call.gather.ended" else None
            ),
            raw=payload,
        )

    async def execute_actions(
        self, event: CallEvent, actions: List[CallAction]
    ) -> Optional[Response]:
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(base_url=self._api_base, headers=headers, timeout=10.0) as client:
            for action in actions:
                await self._send_command(client, event.call_id, action)
        return None  # Telnyx commands are async REST calls, not webhook response bodies

    async def _send_command(
        self, client: httpx.AsyncClient, call_control_id: str, action: CallAction
    ) -> None:
        path = f"/calls/{call_control_id}/actions"
        if isinstance(action, Answer):
            await client.post(f"{path}/answer", json={})
        elif isinstance(action, Speak):
            await client.post(
                f"{path}/speak", json={"payload": action.text, "voice": action.voice or "female"}
            )
        elif isinstance(action, Gather):
            await client.post(
                f"{path}/gather_using_speak",
                json={
                    "payload": action.prompt or "",
                    "valid_digits": "0123456789#*",
                    "max": action.num_digits or 1,
                    "timeout_millis": action.timeout_seconds * 1000,
                },
            )
        elif isinstance(action, StartStream):
            await client.post(f"{path}/streaming_start", json={"stream_url": action.stream_url})
        elif isinstance(action, Dial):
            await client.post(f"{path}/transfer", json={"to": action.to_number})
        elif isinstance(action, (Hangup, Reject)):
            await client.post(f"{path}/hangup", json={})
