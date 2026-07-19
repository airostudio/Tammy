"""Turns a normalized CallEvent into a list of CallActions.

This is the provider-agnostic decision layer: it never touches Twilio
or Telnyx directly, only the types in app.telephony.models. Currently a
placeholder that answers and greets the caller - wiring this into
TammyAssistant/IntentParser so a call can actually route to
appointments/tasks/messages is follow-up work, best done once a
provider account is available to test against a live call.
"""

import logging
from typing import List

from app.telephony.models import Answer, CallAction, CallEvent, CallEventType, Hangup, Speak

logger = logging.getLogger(__name__)


class CallEventHandler:
    async def handle_event(self, event: CallEvent) -> List[CallAction]:
        logger.info(
            "Call event: provider=%s type=%s call_id=%s from=%s",
            event.provider,
            event.event_type,
            event.call_id,
            event.from_number,
        )

        if event.event_type == CallEventType.INITIATED:
            return [
                Answer(),
                Speak(
                    text="Thank you for calling. This is Tammy, your virtual assistant. "
                    "How can I help you today?"
                ),
            ]
        if event.event_type == CallEventType.HANGUP:
            return []
        return [Hangup()]
