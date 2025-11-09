"""Appointment schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AppointmentBase(BaseModel):
    """Base appointment schema"""

    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    duration_minutes: int = 60
    all_day: bool = False
    attendees: List[str] = []
    meeting_url: Optional[str] = None
    conference_room: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""

    user_id: str


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""

    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    all_day: Optional[bool] = None
    attendees: Optional[List[str]] = None
    meeting_url: Optional[str] = None
    conference_room: Optional[str] = None
    status: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""

    id: str
    user_id: str
    end_time: datetime
    status: str
    is_reminder_sent: bool
    is_recurring: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
