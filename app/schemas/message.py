"""Message schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class MessageBase(BaseModel):
    """Base message schema"""

    message_type: str
    direction: str
    from_email: Optional[EmailStr] = None
    from_phone: Optional[str] = None
    to_email: Optional[EmailStr] = None
    to_phone: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    priority: str = "normal"


class MessageCreate(MessageBase):
    """Schema for creating a message"""

    pass


class MessageUpdate(BaseModel):
    """Schema for updating a message"""

    status: Optional[str] = None
    priority: Optional[str] = None
    is_flagged: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class MessageResponse(MessageBase):
    """Schema for message response"""

    id: str
    status: str
    is_flagged: bool
    has_attachments: bool
    sentiment: Optional[str] = None
    category: Optional[str] = None
    requires_action: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
