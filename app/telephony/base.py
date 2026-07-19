"""Common interface every SIP/voice carrier adapter must implement.

Carriers split into two fundamentally different call-control paradigms:

- Response-driven (e.g. Twilio): the webhook's HTTP response body IS the
  instruction set for the call, expressed as markup (TwiML).
- Command-driven (e.g. Telnyx Call Control): the webhook is just a
  notification: instructions are separate authenticated REST calls made
  back to the provider, decoupled from the HTTP response to the webhook.

`execute_actions()` absorbs that difference: response-driven adapters
return a `Response` the router should send back as-is; command-driven
adapters fire their own async command calls and return `None`.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from starlette.responses import Response

from app.telephony.models import CallAction, CallEvent


class TelephonyProvider(ABC):
    """Adapter contract for a single telephony/SIP carrier."""

    name: str

    @abstractmethod
    def verify_signature(self, headers: Dict[str, str], raw_body: bytes, url: str) -> bool:
        """Validate that an inbound webhook actually came from this carrier."""

    @abstractmethod
    def parse_event(self, headers: Dict[str, str], raw_body: bytes) -> CallEvent:
        """Normalize a carrier-specific webhook payload into a CallEvent."""

    @abstractmethod
    async def execute_actions(
        self, event: CallEvent, actions: List[CallAction]
    ) -> Optional[Response]:
        """Carry out the requested actions using this carrier's mechanism.

        Returns a Response to send back to the webhook caller for
        response-driven carriers, or None once the carrier's own
        command API has already been called directly.
        """
