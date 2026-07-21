"""Calendar connection model - stores an OAuth token for one user's
connected external calendar (Google Calendar or Microsoft 365/Outlook)."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class CalendarConnection(Base):
    """One user's OAuth connection to an external calendar provider"""

    __tablename__ = "calendar_connections"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    provider = Column(String, nullable=False)  # google | microsoft
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    # Which calendar to write to, and whose account this is - both
    # provider-supplied, shown in the admin UI so it's clear what's connected.
    external_calendar_id = Column(String, nullable=True)
    external_account_email = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CalendarConnection {self.provider} for user {self.user_id}>"
