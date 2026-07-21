"""Appointment API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment: AppointmentCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new appointment"""
    return await AppointmentService.create_appointment(db, appointment)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str, db: AsyncSession = Depends(get_db)):
    """Get an appointment by ID"""
    appointment = await AppointmentService.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get appointments, optionally filtered by user. Omitting user_id returns all."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    return await AppointmentService.get_user_appointments(db, user_id, start, end)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str, appointment: AppointmentUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an appointment"""
    updated = await AppointmentService.update_appointment(db, appointment_id, appointment)
    if not updated:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(appointment_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an appointment"""
    success = await AppointmentService.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")


@router.get("/user/{user_id}/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(user_id: str, hours: int = 24, db: AsyncSession = Depends(get_db)):
    """Get upcoming appointments for a user"""
    return await AppointmentService.get_upcoming_appointments(db, user_id, hours)


@router.post("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: str, new_start_time: str, db: AsyncSession = Depends(get_db)
):
    """Reschedule an appointment"""
    try:
        new_time = datetime.fromisoformat(new_start_time)
        return await AppointmentService.reschedule_appointment(db, appointment_id, new_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
