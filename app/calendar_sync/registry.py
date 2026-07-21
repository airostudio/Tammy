"""Selects a CalendarProvider adapter by name."""

from typing import Dict, Optional, Type

from app.calendar_sync.base import CalendarProvider
from app.calendar_sync.providers.google_calendar import GoogleCalendarProvider
from app.calendar_sync.providers.microsoft_graph import MicrosoftGraphProvider
from app.config import Settings, get_settings

_PROVIDER_CLASSES: Dict[str, Type[CalendarProvider]] = {
    "google": GoogleCalendarProvider,
    "microsoft": MicrosoftGraphProvider,
}


def get_calendar_provider(name: str, settings: Optional[Settings] = None) -> CalendarProvider:
    """Instantiate the OAuth calendar adapter for `name` ("google" | "microsoft")"""
    settings = settings or get_settings()
    provider_cls = _PROVIDER_CLASSES.get(name.lower())
    if provider_cls is None:
        raise ValueError(f"Unknown calendar provider '{name}'. Supported: {sorted(_PROVIDER_CLASSES)}")
    return provider_cls(settings)
