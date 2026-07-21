"""Common interface every OAuth calendar integration must implement.

This covers the two OAuth-based providers (Google Calendar, Microsoft
Graph) that push events into a specific connected calendar and need a
stored, refreshable access token. The iCal/.ics export is a separate,
simpler no-OAuth path (app/calendar_sync/providers/ical_export.py) - it
doesn't fit this interface since there's no connection or token
involved, just a read-only feed any calendar app can subscribe to.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CalendarEvent:
    """Normalized appointment data handed to a provider to push/update."""

    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)


@dataclass
class OAuthToken:
    """Result of an OAuth code exchange or token refresh."""

    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]
    account_email: Optional[str] = None
    calendar_id: Optional[str] = None


class CalendarProvider(ABC):
    """Adapter contract for a single OAuth calendar integration."""

    name: str

    @abstractmethod
    def get_authorize_url(self, state: str, redirect_uri: str) -> str:
        """Build the URL to send the user to in order to grant calendar access."""

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthToken:
        """Exchange an OAuth authorization code for tokens."""

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Use a refresh token to obtain a new access token."""

    @abstractmethod
    async def push_event(self, access_token: str, calendar_id: Optional[str], event: CalendarEvent) -> str:
        """Create the event on the external calendar. Returns the external event id."""

    @abstractmethod
    async def update_event(
        self, access_token: str, calendar_id: Optional[str], external_event_id: str, event: CalendarEvent
    ) -> None:
        """Update an existing external event."""

    @abstractmethod
    async def delete_event(self, access_token: str, calendar_id: Optional[str], external_event_id: str) -> None:
        """Delete/cancel an existing external event."""
