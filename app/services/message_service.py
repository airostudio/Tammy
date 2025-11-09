"""Message service for communication management"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from typing import List, Optional
import uuid

from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate


class MessageService:
    """Service for managing messages and communications"""

    @staticmethod
    async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
        """Create a new message"""
        # Create snippet from body
        snippet = None
        if message.body:
            snippet = message.body[:200] + "..." if len(message.body) > 200 else message.body

        db_message = Message(
            id=str(uuid.uuid4()),
            message_type=message.message_type,
            direction=message.direction,
            from_email=message.from_email,
            from_phone=message.from_phone,
            to_email=message.to_email,
            to_phone=message.to_phone,
            subject=message.subject,
            body=message.body,
            snippet=snippet,
            priority=message.priority,
            received_at=datetime.utcnow() if message.direction == "inbound" else None,
            sent_at=datetime.utcnow() if message.direction == "outbound" else None,
        )

        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def get_message(db: AsyncSession, message_id: str) -> Optional[Message]:
        """Get a message by ID"""
        result = await db.execute(select(Message).where(Message.id == message_id))
        message = result.scalar_one_or_none()

        # Mark as read if currently unread
        if message and message.status == "unread":
            message.status = "read"
            message.read_at = datetime.utcnow()
            await db.commit()
            await db.refresh(message)

        return message

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        message_type: Optional[str] = None,
        status: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Message]:
        """Get messages with optional filtering"""
        query = select(Message)

        if message_type:
            query = query.where(Message.message_type == message_type)
        if status:
            query = query.where(Message.status == status)
        if direction:
            query = query.where(Message.direction == direction)

        query = query.order_by(Message.received_at.desc().nullslast(), Message.sent_at.desc().nullslast())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_message(
        db: AsyncSession, message_id: str, message_update: MessageUpdate
    ) -> Optional[Message]:
        """Update a message"""
        db_message = await MessageService.get_message(db, message_id)
        if not db_message:
            return None

        update_data = message_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_message, field, value)

        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: str) -> bool:
        """Delete a message"""
        db_message = await MessageService.get_message(db, message_id)
        if not db_message:
            return False

        await db.delete(db_message)
        await db.commit()
        return True

    @staticmethod
    async def get_unread_messages(db: AsyncSession) -> List[Message]:
        """Get all unread messages"""
        query = select(Message).where(Message.status == "unread").order_by(Message.received_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_flagged_messages(db: AsyncSession) -> List[Message]:
        """Get all flagged messages"""
        query = select(Message).where(Message.is_flagged == True).order_by(Message.received_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def search_messages(db: AsyncSession, query_text: str) -> List[Message]:
        """Search messages by subject or body"""
        query = select(Message).where(
            or_(
                Message.subject.ilike(f"%{query_text}%"),
                Message.body.ilike(f"%{query_text}%"),
            )
        ).order_by(Message.received_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def mark_as_read(db: AsyncSession, message_id: str) -> Optional[Message]:
        """Mark a message as read"""
        db_message = await MessageService.get_message(db, message_id)
        if not db_message:
            return None

        db_message.status = "read"
        db_message.read_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def archive_message(db: AsyncSession, message_id: str) -> Optional[Message]:
        """Archive a message"""
        db_message = await MessageService.get_message(db, message_id)
        if not db_message:
            return None

        db_message.status = "archived"

        await db.commit()
        await db.refresh(db_message)
        return db_message
