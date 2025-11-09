"""Visitor service for visitor and call management"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.models.visitor import Visitor
from app.schemas.visitor import VisitorCreate, VisitorUpdate


class VisitorService:
    """Service for managing visitors and calls"""

    @staticmethod
    async def create_visitor(db: AsyncSession, visitor: VisitorCreate) -> Visitor:
        """Create a new visitor record"""
        db_visitor = Visitor(
            id=str(uuid.uuid4()),
            full_name=visitor.full_name,
            company=visitor.company,
            email=visitor.email,
            phone_number=visitor.phone_number,
            visit_type=visitor.visit_type,
            purpose=visitor.purpose,
            host_name=visitor.host_name,
            host_department=visitor.host_department,
            scheduled_time=visitor.scheduled_time,
            location=visitor.location,
            conference_room=visitor.conference_room,
        )

        db.add(db_visitor)
        await db.commit()
        await db.refresh(db_visitor)
        return db_visitor

    @staticmethod
    async def get_visitor(db: AsyncSession, visitor_id: str) -> Optional[Visitor]:
        """Get a visitor by ID"""
        result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_visitors(
        db: AsyncSession, status: Optional[str] = None, visit_type: Optional[str] = None
    ) -> List[Visitor]:
        """Get all visitors, optionally filtered by status and type"""
        query = select(Visitor)

        if status:
            query = query.where(Visitor.status == status)
        if visit_type:
            query = query.where(Visitor.visit_type == visit_type)

        query = query.order_by(Visitor.scheduled_time.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_visitor(
        db: AsyncSession, visitor_id: str, visitor_update: VisitorUpdate
    ) -> Optional[Visitor]:
        """Update a visitor record"""
        db_visitor = await VisitorService.get_visitor(db, visitor_id)
        if not db_visitor:
            return None

        update_data = visitor_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_visitor, field, value)

        await db.commit()
        await db.refresh(db_visitor)
        return db_visitor

    @staticmethod
    async def check_in_visitor(db: AsyncSession, visitor_id: str, badge_number: Optional[str] = None) -> Optional[Visitor]:
        """Check in a visitor"""
        db_visitor = await VisitorService.get_visitor(db, visitor_id)
        if not db_visitor:
            return None

        db_visitor.status = "checked_in"
        db_visitor.check_in_time = datetime.utcnow()
        if badge_number:
            db_visitor.badge_number = badge_number

        await db.commit()
        await db.refresh(db_visitor)
        return db_visitor

    @staticmethod
    async def check_out_visitor(db: AsyncSession, visitor_id: str) -> Optional[Visitor]:
        """Check out a visitor"""
        db_visitor = await VisitorService.get_visitor(db, visitor_id)
        if not db_visitor:
            return None

        db_visitor.status = "checked_out"
        db_visitor.check_out_time = datetime.utcnow()

        await db.commit()
        await db.refresh(db_visitor)
        return db_visitor

    @staticmethod
    async def get_current_visitors(db: AsyncSession) -> List[Visitor]:
        """Get all currently checked-in visitors"""
        query = select(Visitor).where(Visitor.status == "checked_in").order_by(Visitor.check_in_time.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_scheduled_visitors(db: AsyncSession, hours: int = 24) -> List[Visitor]:
        """Get visitors scheduled within the next N hours"""
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)

        query = select(Visitor).where(
            and_(
                Visitor.status == "scheduled",
                Visitor.scheduled_time >= now,
                Visitor.scheduled_time <= end_time,
            )
        ).order_by(Visitor.scheduled_time)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_visitors_by_host(db: AsyncSession, host_name: str) -> List[Visitor]:
        """Get all visitors for a specific host"""
        query = select(Visitor).where(Visitor.host_name == host_name).order_by(Visitor.scheduled_time.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete_visitor(db: AsyncSession, visitor_id: str) -> bool:
        """Delete a visitor record"""
        db_visitor = await VisitorService.get_visitor(db, visitor_id)
        if not db_visitor:
            return False

        await db.delete(db_visitor)
        await db.commit()
        return True
