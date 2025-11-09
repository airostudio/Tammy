"""Appointment model"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Appointment(Base):
    """Appointment model for calendar management"""

    __tablename__ = "appointments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    all_day = Column(Boolean, default=False)

    # Attendees stored as JSON array
    attendees = Column(JSON, default=list)

    # Meeting details
    meeting_url = Column(String, nullable=True)
    conference_room = Column(String, nullable=True)

    # Status
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    is_reminder_sent = Column(Boolean, default=False)

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)  # RRULE format

    # Metadata
    created_by = Column(String, default="tammy")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment {self.title} at {self.start_time}>"
