"""Pydantic schemas for request/response validation"""

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.visitor import VisitorCreate, VisitorUpdate, VisitorResponse
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.schemas.chat import ChatRequest, ChatResponse

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "VisitorCreate",
    "VisitorUpdate",
    "VisitorResponse",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "ChatRequest",
    "ChatResponse",
]
