"""API routes"""

from fastapi import APIRouter
from app.api import appointments, contacts, tasks, visitors, messages, chat

api_router = APIRouter()

# Include all route modules
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(visitors.router, prefix="/visitors", tags=["visitors"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
