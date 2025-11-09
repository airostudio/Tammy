"""User schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str
    full_name: str
    timezone: str = "UTC"
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""

    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
