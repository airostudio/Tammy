"""Chat API endpoints for Tammy AI"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.assistant import TammyAssistant

router = APIRouter()

# Global assistant instance (in production, use session-based instances)
assistant = TammyAssistant()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with Tammy AI assistant"""
    try:
        # Process the message
        response = await assistant.process_message(request.message, request.context)

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


@router.get("/history")
async def get_chat_history(session_id: str = None):
    """Get chat history for a session"""
    history = assistant.get_history()
    return {"history": history}


@router.delete("/history")
async def clear_chat_history(session_id: str = None):
    """Clear chat history for a session"""
    assistant.clear_history()
    return {"message": "Chat history cleared"}


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
