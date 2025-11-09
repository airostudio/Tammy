"""Chat schemas for AI conversation"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Schema for chat requests to Tammy"""

    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat responses from Tammy"""

    response: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = datetime.utcnow()

    class Config:
        from_attributes = True
