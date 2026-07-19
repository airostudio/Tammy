"""Provider-agnostic call events and call actions.

Every carrier adapter parses its own webhook payload into a `CallEvent`
and translates a list of `CallAction` objects into whatever mechanism
that carrier uses to control the call. Nothing outside `app.telephony`
should need to know which carrier is in use.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallEventType(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    DTMF = "dtmf"
    SPEECH = "speech"
    RECORDING = "recording"
    HANGUP = "hangup"
    UNKNOWN = "unknown"


@dataclass
class CallEvent:
    """Normalized representation of an inbound webhook from any carrier."""

    provider: str
    event_type: CallEventType
    call_id: str
    from_number: str
    to_number: str
    direction: CallDirection
    dtmf_digits: Optional[str] = None
    speech_result: Optional[str] = None
    # Original provider payload, kept for provider-specific edge cases that
    # haven't been normalized yet - avoid relying on this outside an adapter.
    raw: Dict[str, Any] = field(default_factory=dict)


class CallAction:
    """Marker base class for provider-agnostic call actions."""


@dataclass
class Answer(CallAction):
    """Accept an inbound call."""


@dataclass
class Speak(CallAction):
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None


@dataclass
class Gather(CallAction):
    """Collect DTMF digits and/or speech from the caller."""

    prompt: Optional[str] = None
    input_type: str = "dtmf"  # "dtmf" | "speech"
    num_digits: Optional[int] = None
    timeout_seconds: int = 5


@dataclass
class StartStream(CallAction):
    """Open a bidirectional media stream (e.g. for live STT/TTS)."""

    stream_url: str


@dataclass
class Dial(CallAction):
    """Transfer/bridge the call to another number."""

    to_number: str


@dataclass
class Hangup(CallAction):
    reason: Optional[str] = None


@dataclass
class Reject(CallAction):
    reason: Optional[str] = None
