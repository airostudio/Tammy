"""Visitor schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class VisitorBase(BaseModel):
    """Base visitor schema"""

    full_name: str
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    visit_type: str = "in_person"
    purpose: Optional[str] = None
    host_name: str
    host_department: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    location: Optional[str] = None
    conference_room: Optional[str] = None


class VisitorCreate(VisitorBase):
    """Schema for creating a visitor"""

    pass


class VisitorUpdate(BaseModel):
    """Schema for updating a visitor"""

    status: Optional[str] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    badge_number: Optional[str] = None
    id_verified: Optional[bool] = None
    nda_signed: Optional[bool] = None
    notes: Optional[str] = None


class VisitorResponse(VisitorBase):
    """Schema for visitor response"""

    id: str
    status: str
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    badge_number: Optional[str] = None
    host_notified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
