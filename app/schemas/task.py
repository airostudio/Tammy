"""Task schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    """Base task schema"""

    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    project: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    assigned_to: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a task"""

    user_id: str


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    project: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task response"""

    id: str
    user_id: str
    status: str
    progress_percentage: int
    start_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
