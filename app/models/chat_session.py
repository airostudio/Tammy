"""Chat session model - carries an in-progress chat intent across requests.

The chat endpoint is stateless HTTP (and may run as separate serverless
invocations), so any "what were we talking about" memory has to be
persisted here rather than kept on a Python object in memory - an
in-memory instance or process-wide singleton would only ever work by
accident on a single long-lived dev server, and silently lose context
the moment there's more than one worker/instance.
"""

from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from app.database import Base


class ChatSession(Base):
    """One row per chat session_id, holding the intent Tammy is still
    waiting on more information for (if any). Cleared once that intent
    is either completed or abandoned for a new one.
    """

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)  # the client-supplied session_id

    pending_intent = Column(String, nullable=True)
    pending_entities = Column(JSON, nullable=True)
    pending_message = Column(String, nullable=True)  # original_message so far, for context

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ChatSession {self.id} pending={self.pending_intent}>"
