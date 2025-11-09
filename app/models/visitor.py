"""Visitor model"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from datetime import datetime
from app.database import Base


class Visitor(Base):
    """Visitor model for visitor and call management"""

    __tablename__ = "visitors"

    id = Column(String, primary_key=True, index=True)

    # Visitor Information
    full_name = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Visit Details
    visit_type = Column(String, default="in_person")  # in_person, call, video_call
    purpose = Column(Text, nullable=True)
    host_name = Column(String, nullable=False)  # Person they're visiting
    host_department = Column(String, nullable=True)

    # Timing
    scheduled_time = Column(DateTime, nullable=True)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)

    # Status
    status = Column(String, default="scheduled", index=True)  # scheduled, checked_in, checked_out, no_show, cancelled

    # Location and Resources
    location = Column(String, nullable=True)  # Office, floor, room
    conference_room = Column(String, nullable=True)
    parking_spot = Column(String, nullable=True)

    # Security
    badge_number = Column(String, nullable=True)
    id_verified = Column(Boolean, default=False)
    nda_signed = Column(Boolean, default=False)

    # Call Details (if visit_type is call)
    call_duration_minutes = Column(String, nullable=True)
    call_notes = Column(Text, nullable=True)

    # Notes and Attachments
    notes = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)

    # Notification
    host_notified = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Visitor {self.full_name} [{self.status}]>"
