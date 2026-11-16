"""Chat API endpoints for Tammy AI"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.assistant import TammyAssistant

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with Tammy AI assistant.

    A fresh assistant is created for every request - it holds no state
    of its own. Any memory of an in-progress, not-yet-complete request
    (e.g. "Schedule a meeting with Mike" before a date/time has been
    given) is carried across requests via `request.session_id`, backed
    by the chat_sessions table (see ChatSessionService) rather than a
    Python object - the previous version of this endpoint kept a single
    module-level TammyAssistant shared by every caller, which not only
    couldn't survive more than one worker process but meant every
    user's conversation state lived in the same shared instance.
    """
    try:
        response = await assistant_for_request().process_message(
            request.message, db, request.context, request.session_id
        )

        return ChatResponse(
            response=response["response"],
            intent=response.get("intent"),
            entities=response.get("entities"),
            actions=response.get("actions"),
            confidence=response.get("confidence"),
            suggestions=response.get("suggestions"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


def assistant_for_request() -> TammyAssistant:
    """A new assistant per request - see the chat() docstring for why."""
    return TammyAssistant()


@router.get("/capabilities")
async def get_capabilities():
    """Get Tammy's capabilities"""
    return {
        "capabilities": [
            {
                "category": "Calendar Management",
                "features": [
                    "Schedule appointments and meetings",
                    "Check availability",
                    "Send reminders",
                    "Reschedule conflicts",
                ],
            },
            {
                "category": "Task Management",
                "features": [
                    "Create and track tasks",
                    "Set priorities and deadlines",
                    "Monitor progress",
                    "Project coordination",
                ],
            },
            {
                "category": "Contact Management",
                "features": [
                    "Store contact information",
                    "Search contacts",
                    "Track relationships",
                    "Remember important dates",
                ],
            },
            {
                "category": "Visitor Management",
                "features": [
                    "Check-in/check-out visitors",
                    "Maintain visitor logs",
                    "Schedule visitor appointments",
                    "Notify hosts",
                ],
            },
            {
                "category": "Communication",
                "features": [
                    "Manage messages and emails",
                    "Filter and prioritize",
                    "Draft responses",
                    "Handle inquiries",
                ],
            },
        ],
        "examples": [
            "Schedule a meeting with John tomorrow at 2pm",
            "What's on my calendar today?",
            "Create a task to review proposal by Friday",
            "Find contact info for Sarah",
            "Check in visitor Jane Doe",
            "Show my unread messages",
        ],
    }
