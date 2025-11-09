"""Contact schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List, Dict


class ContactBase(BaseModel):
    """Base contact schema"""

    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    mobile_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    birthday: Optional[date] = None
    anniversary: Optional[date] = None
    relationship_type: Optional[str] = None
    priority: str = "normal"
    notes: Optional[str] = None
    tags: List[str] = []


class ContactCreate(ContactBase):
    """Schema for creating a contact"""

    user_id: str


class ContactUpdate(BaseModel):
    """Schema for updating a contact"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    mobile_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    birthday: Optional[date] = None
    anniversary: Optional[date] = None
    relationship_type: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None


class ContactResponse(ContactBase):
    """Schema for contact response"""

    id: str
    user_id: str
    full_name: str
    is_favorite: bool
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
