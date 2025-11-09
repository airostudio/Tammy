"""Message model"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from datetime import datetime
from app.database import Base


class Message(Base):
    """Message model for communication management"""

    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)

    # Message Type
    message_type = Column(String, nullable=False, index=True)  # email, sms, call, chat, note
    direction = Column(String, nullable=False)  # inbound, outbound

    # Sender and Recipient
    from_name = Column(String, nullable=True)
    from_email = Column(String, nullable=True, index=True)
    from_phone = Column(String, nullable=True)
    to_name = Column(String, nullable=True)
    to_email = Column(String, nullable=True, index=True)
    to_phone = Column(String, nullable=True)

    # Message Content
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    snippet = Column(String, nullable=True)  # First 200 chars for preview

    # Status and Priority
    status = Column(String, default="unread", index=True)  # unread, read, replied, archived, deleted
    priority = Column(String, default="normal")  # low, normal, high, urgent
    is_flagged = Column(Boolean, default=False)
    is_spam = Column(Boolean, default=False)

    # Threading
    thread_id = Column(String, nullable=True, index=True)
    in_reply_to = Column(String, nullable=True)

    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Attachments
    has_attachments = Column(Boolean, default=False)
    attachments = Column(JSON, default=list)

    # AI Processing
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    category = Column(String, nullable=True)  # meeting_request, question, complaint, etc.
    requires_action = Column(Boolean, default=False)
    action_type = Column(String, nullable=True)  # reply, schedule, escalate, etc.
    ai_draft_reply = Column(Text, nullable=True)

    # Tags and Labels
    tags = Column(JSON, default=list)
    labels = Column(JSON, default=list)

    # External IDs
    external_id = Column(String, nullable=True)  # Email provider message ID

    # Notes
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.message_type} from {self.from_email or self.from_phone} [{self.status}]>"
