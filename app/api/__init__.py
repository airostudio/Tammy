"""API routes"""

from fastapi import APIRouter, Depends
from app.api import appointments, contacts, tasks, visitors, messages, chat, telephony, admin, calendar
from app.api.deps import require_admin

api_router = APIRouter()

# Admin session endpoints (login is necessarily public - you can't be
# logged in yet when you're logging in)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Data endpoints - gated behind the shared admin password, since this is
# business data (appointments, contacts, tasks, visitors, messages) with
# no other access control in front of it.
api_router.include_router(
    appointments.router, prefix="/appointments", tags=["appointments"], dependencies=[Depends(require_admin)]
)
api_router.include_router(
    contacts.router, prefix="/contacts", tags=["contacts"], dependencies=[Depends(require_admin)]
)
api_router.include_router(
    tasks.router, prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_admin)]
)
api_router.include_router(
    visitors.router, prefix="/visitors", tags=["visitors"], dependencies=[Depends(require_admin)]
)
api_router.include_router(
    messages.router, prefix="/messages", tags=["messages"], dependencies=[Depends(require_admin)]
)

# Public endpoints - used by the marketing/demo frontend and carrier webhooks
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(telephony.router, prefix="/telephony", tags=["telephony"])

# Mixed: the iCal feed is intentionally public (token-gated, see
# app/api/calendar.py), feed-url is admin-gated on its own route.
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
