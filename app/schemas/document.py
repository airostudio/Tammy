"""Document schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DocumentBase(BaseModel):
    """Base document schema"""

    title: str
    description: Optional[str] = None
    file_name: str
    file_type: str
    category: Optional[str] = None
    tags: List[str] = []


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""

    file_path: str
    file_size: int
    mime_type: str
    owner_id: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""

    id: str
    file_path: str
    file_size: int
    mime_type: str
    owner_id: Optional[str] = None
    status: str
    version: str
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
