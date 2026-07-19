"""Twilio adapter - response-driven call control via TwiML.

Signature verification follows Twilio's documented algorithm exactly
(https://www.twilio.com/docs/usage/webhooks/webhooks-security) without
depending on the `twilio` SDK, since the algorithm is a straightforward
HMAC-SHA1 over the request URL and sorted form parameters.
"""

import base64
import hashlib
import hmac
from typing import Dict, List, Optional
from urllib.parse import parse_qsl
from xml.sax.saxutils import escape as xml_escape

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

_STATUS_TO_EVENT_TYPE = {
    "queued": CallEventType.INITIATED,
    "ringing": CallEventType.RINGING,
    "in-progress": CallEventType.ANSWERED,
    "completed": CallEventType.HANGUP,
    "busy": CallEventType.HANGUP,
    "failed": CallEventType.HANGUP,
    "no-answer": CallEventType.HANGUP,
    "canceled": CallEventType.HANGUP,
}


class TwilioProvider(TelephonyProvider):
    name = "twilio"

    def __init__(self, settings):
        self._auth_token = settings.twilio_auth_token

    def verify_signature(self, headers: Dict[str, str], raw_body: bytes, url: str) -> bool:
        signature = headers.get("x-twilio-signature") or headers.get("X-Twilio-Signature")
        if not signature or not self._auth_token:
            return False
        params = dict(parse_qsl(raw_body.decode("utf-8")))
        data = url + "".join(f"{key}{value}" for key, value in sorted(params.items()))
        expected = base64.b64encode(
            hmac.new(self._auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
        ).decode("utf-8")
        return hmac.compare_digest(expected, signature)

    def parse_event(self, headers: Dict[str, str], raw_body: bytes) -> CallEvent:
        params = dict(parse_qsl(raw_body.decode("utf-8")))
        status = params.get("CallStatus", "")
        event_type = _STATUS_TO_EVENT_TYPE.get(status, CallEventType.UNKNOWN)
        if params.get("Digits"):
            event_type = CallEventType.DTMF
        if params.get("SpeechResult"):
            event_type = CallEventType.SPEECH

        direction_raw = params.get("Direction", "inbound")
        direction = (
            CallDirection.INBOUND if direction_raw.startswith("inbound") else CallDirection.OUTBOUND
        )

        return CallEvent(
            provider=self.name,
            event_type=event_type,
            call_id=params.get("CallSid", ""),
            from_number=params.get("From", ""),
            to_number=params.get("To", ""),
            direction=direction,
            dtmf_digits=params.get("Digits"),
            speech_result=params.get("SpeechResult"),
            raw=params,
        )

    async def execute_actions(
        self, event: CallEvent, actions: List[CallAction]
    ) -> Optional[Response]:
        return Response(content=self._build_twiml(actions), media_type="application/xml")

    def _build_twiml(self, actions: List[CallAction]) -> str:
        parts = ['<?xml version="1.0" encoding="UTF-8"?>', "<Response>"]
        for action in actions:
            if isinstance(action, Answer):
                continue  # Twilio has already connected the call by the time the webhook fires
            elif isinstance(action, Speak):
                parts.append(f"<Say>{xml_escape(action.text)}</Say>")
            elif isinstance(action, Gather):
                attrs = f'input="{action.input_type}" timeout="{action.timeout_seconds}"'
                if action.num_digits:
                    attrs += f' numDigits="{action.num_digits}"'
                if action.prompt:
                    parts.append(f"<Gather {attrs}><Say>{xml_escape(action.prompt)}</Say></Gather>")
                else:
                    parts.append(f"<Gather {attrs}/>")
            elif isinstance(action, StartStream):
                parts.append(f'<Start><Stream url="{xml_escape(action.stream_url)}"/></Start>')
            elif isinstance(action, Dial):
                parts.append(f"<Dial>{xml_escape(action.to_number)}</Dial>")
            elif isinstance(action, (Hangup, Reject)):
                parts.append("<Hangup/>")
        parts.append("</Response>")
        return "".join(parts)
