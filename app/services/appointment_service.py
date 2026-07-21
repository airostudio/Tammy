"""Appointment service for calendar management"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    """Service for managing appointments and calendar"""

    @staticmethod
    async def create_appointment(db: AsyncSession, appointment: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        # Calculate end time
        end_time = appointment.start_time + timedelta(minutes=appointment.duration_minutes)

        db_appointment = Appointment(
            id=str(uuid.uuid4()),
            user_id=appointment.user_id,
            title=appointment.title,
            description=appointment.description,
            location=appointment.location,
            start_time=appointment.start_time,
            end_time=end_time,
            duration_minutes=appointment.duration_minutes,
            all_day=appointment.all_day,
            attendees=appointment.attendees,
            meeting_url=appointment.meeting_url,
            conference_room=appointment.conference_room,
        )

        db.add(db_appointment)
        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment

    @staticmethod
    async def get_appointment(db: AsyncSession, appointment_id: str) -> Optional[Appointment]:
        """Get an appointment by ID"""
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_appointments(
        db: AsyncSession,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Appointment]:
        """Get appointments, optionally filtered by user and date range.
        Omitting user_id returns appointments across all users (admin use)."""
        query = select(Appointment)

        if user_id:
            query = query.where(Appointment.user_id == user_id)
        if start_date:
            query = query.where(Appointment.start_time >= start_date)
        if end_date:
            query = query.where(Appointment.start_time <= end_date)

        query = query.order_by(Appointment.start_time)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_appointment(
        db: AsyncSession, appointment_id: str, appointment_update: AppointmentUpdate
    ) -> Optional[Appointment]:
        """Update an appointment"""
        db_appointment = await AppointmentService.get_appointment(db, appointment_id)
        if not db_appointment:
            return None

        update_data = appointment_update.model_dump(exclude_unset=True)

        # Recalculate end_time if start_time or duration changed
        if "start_time" in update_data or "duration_minutes" in update_data:
            start_time = update_data.get("start_time", db_appointment.start_time)
            duration = update_data.get("duration_minutes", db_appointment.duration_minutes)
            update_data["end_time"] = start_time + timedelta(minutes=duration)

        for field, value in update_data.items():
            setattr(db_appointment, field, value)

        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment

    @staticmethod
    async def delete_appointment(db: AsyncSession, appointment_id: str) -> bool:
        """Delete an appointment"""
        db_appointment = await AppointmentService.get_appointment(db, appointment_id)
        if not db_appointment:
            return False

        await db.delete(db_appointment)
        await db.commit()
        return True

    @staticmethod
    async def check_availability(
        db: AsyncSession, user_id: str, start_time: datetime, duration_minutes: int
    ) -> bool:
        """Check if a time slot is available"""
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Check for conflicting appointments
        query = select(Appointment).where(
            and_(
                Appointment.user_id == user_id,
                Appointment.status != "cancelled",
                or_(
                    and_(Appointment.start_time <= start_time, Appointment.end_time > start_time),
                    and_(Appointment.start_time < end_time, Appointment.end_time >= end_time),
                    and_(Appointment.start_time >= start_time, Appointment.end_time <= end_time),
                ),
            )
        )

        result = await db.execute(query)
        conflicts = result.scalars().all()

        return len(conflicts) == 0

    @staticmethod
    async def get_upcoming_appointments(db: AsyncSession, user_id: str, hours: int = 24) -> List[Appointment]:
        """Get upcoming appointments within the next N hours"""
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)

        query = (
            select(Appointment)
            .where(
                and_(
                    Appointment.user_id == user_id,
                    Appointment.start_time >= now,
                    Appointment.start_time <= end_time,
                    Appointment.status == "scheduled",
                )
            )
            .order_by(Appointment.start_time)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def reschedule_appointment(
        db: AsyncSession, appointment_id: str, new_start_time: datetime
    ) -> Optional[Appointment]:
        """Reschedule an appointment to a new time"""
        db_appointment = await AppointmentService.get_appointment(db, appointment_id)
        if not db_appointment:
            return None

        # Check availability at new time
        is_available = await AppointmentService.check_availability(
            db, db_appointment.user_id, new_start_time, db_appointment.duration_minutes
        )

        if not is_available:
            raise ValueError("Time slot not available")

        db_appointment.start_time = new_start_time
        db_appointment.end_time = new_start_time + timedelta(minutes=db_appointment.duration_minutes)
        db_appointment.status = "rescheduled"

        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment
