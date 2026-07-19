"""Selects a TelephonyProvider adapter by name.

Swapping the active carrier for outbound-initiated calls is a config
change (`TELEPHONY_PROVIDER`); each carrier also gets its own webhook
path (e.g. /api/telephony/webhook/telnyx) so multiple carriers can run
side by side for regional least-cost-routing or failover.
"""

from typing import Dict, Optional, Type

from app.config import Settings, get_settings
from app.telephony.base import TelephonyProvider
from app.telephony.providers.telnyx_provider import TelnyxProvider
from app.telephony.providers.twilio_provider import TwilioProvider

_PROVIDER_CLASSES: Dict[str, Type[TelephonyProvider]] = {
    "twilio": TwilioProvider,
    "telnyx": TelnyxProvider,
}


def get_telephony_provider(name: Optional[str] = None, settings: Optional[Settings] = None) -> TelephonyProvider:
    """Instantiate the adapter for `name` (default: settings.telephony_provider)."""
    settings = settings or get_settings()
    provider_name = (name or settings.telephony_provider).lower()
    provider_cls = _PROVIDER_CLASSES.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown telephony provider '{provider_name}'. Supported: {sorted(_PROVIDER_CLASSES)}"
        )
    return provider_cls(settings)
