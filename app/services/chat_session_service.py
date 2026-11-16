"""Chat session service - persists the chat assistant's in-progress intent
(the one real piece of "context" a follow-up message needs) across requests.
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_session import ChatSession

# A pending intent older than this is treated as abandoned - the user moved
# on (or just never came back), so a stray "yes" three hours later shouldn't
# resurrect a half-forgotten appointment request.
PENDING_INTENT_TTL = timedelta(minutes=30)


def _serialize_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    """JSON can't hold a date object - wrap it so it survives the round trip."""
    serialized = {}
    for key, value in entities.items():
        if isinstance(value, date):
            serialized[key] = {"__date__": value.isoformat()}
        else:
            serialized[key] = value
    return serialized


def _deserialize_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    deserialized = {}
    for key, value in entities.items():
        if isinstance(value, dict) and "__date__" in value:
            deserialized[key] = date.fromisoformat(value["__date__"])
        else:
            deserialized[key] = value
    return deserialized


class ChatSessionService:
    """Get/set/clear the one pending intent a chat session is waiting on."""

    @staticmethod
    async def get_pending(db: AsyncSession, session_id: str) -> Optional[Dict[str, Any]]:
        if not session_id:
            return None

        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = result.scalar_one_or_none()
        if session is None or session.pending_intent is None:
            return None

        if session.updated_at and datetime.utcnow() - session.updated_at > PENDING_INTENT_TTL:
            await ChatSessionService.clear(db, session_id)
            return None

        return {
            "intent": session.pending_intent,
            "entities": _deserialize_entities(session.pending_entities or {}),
            "original_message": session.pending_message or "",
        }

    @staticmethod
    async def set_pending(
        db: AsyncSession,
        session_id: str,
        intent: str,
        entities: Dict[str, Any],
        original_message: str,
    ) -> None:
        if not session_id:
            return

        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = result.scalar_one_or_none()
        if session is None:
            session = ChatSession(id=session_id)
            db.add(session)

        session.pending_intent = intent
        session.pending_entities = _serialize_entities(entities)
        session.pending_message = original_message
        session.updated_at = datetime.utcnow()
        await db.commit()

    @staticmethod
    async def clear(db: AsyncSession, session_id: str) -> None:
        if not session_id:
            return

        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = result.scalar_one_or_none()
        if session is not None:
            session.pending_intent = None
            session.pending_entities = None
            session.pending_message = None
            await db.commit()
