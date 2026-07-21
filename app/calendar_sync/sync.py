"""Pushes appointment changes out to any calendars the user has connected.

Best-effort and one-way (Tammy -> calendar): a sync failure is logged
and never blocks the appointment itself from being created/updated/
deleted - the calendar connection is a nice-to-have layered on top of
the source of truth (Tammy's own database), not a dependency of it.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.calendar_sync.base import CalendarEvent, OAuthToken
from app.calendar_sync.registry import get_calendar_provider
from app.models.calendar_connection import CalendarConnection

logger = logging.getLogger(__name__)


def _to_calendar_event(appointment) -> CalendarEvent:
    return CalendarEvent(
        id=appointment.id,
        title=appointment.title,
        description=appointment.description,
        location=appointment.location,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        attendees=appointment.attendees or [],
    )


async def _get_connections(db: AsyncSession, user_id: str):
    result = await db.execute(select(CalendarConnection).where(CalendarConnection.user_id == user_id))
    return list(result.scalars().all())


async def _valid_access_token(db: AsyncSession, connection: CalendarConnection) -> Optional[str]:
    """Refresh the stored token if it looks expired, persisting the new one."""
    if connection.token_expires_at and connection.token_expires_at <= datetime.utcnow():
        if not connection.refresh_token:
            return None
        try:
            provider = get_calendar_provider(connection.provider)
            token = await provider.refresh_access_token(connection.refresh_token)
        except Exception:
            logger.exception("Failed to refresh %s calendar token", connection.provider)
            return None

        connection.access_token = token.access_token
        connection.refresh_token = token.refresh_token or connection.refresh_token
        connection.token_expires_at = token.expires_at
        await db.commit()

    return connection.access_token


async def save_calendar_connection(
    db: AsyncSession, user_id: str, provider_name: str, token: OAuthToken
) -> CalendarConnection:
    """Create or replace the stored connection for this user+provider"""
    result = await db.execute(
        select(CalendarConnection).where(
            CalendarConnection.user_id == user_id, CalendarConnection.provider == provider_name
        )
    )
    connection = result.scalar_one_or_none()
    if connection is None:
        connection = CalendarConnection(id=str(uuid.uuid4()), user_id=user_id, provider=provider_name)
        db.add(connection)

    connection.access_token = token.access_token
    connection.refresh_token = token.refresh_token
    connection.token_expires_at = token.expires_at
    connection.external_calendar_id = token.calendar_id
    connection.external_account_email = token.account_email

    await db.commit()
    await db.refresh(connection)
    return connection


async def sync_appointment_created(db: AsyncSession, appointment) -> None:
    """Push a newly-created appointment to every connected calendar.

    Appointment tracks only one (provider, external_event_id) pair, so if
    multiple calendars are connected, every one gets the event but only
    the first successful push is remembered for future updates/deletes.
    """
    connections = await _get_connections(db, appointment.user_id)
    for connection in connections:
        access_token = await _valid_access_token(db, connection)
        if not access_token:
            continue
        try:
            provider = get_calendar_provider(connection.provider)
            external_id = await provider.push_event(
                access_token, connection.external_calendar_id, _to_calendar_event(appointment)
            )
            if not appointment.external_calendar_provider:
                appointment.external_calendar_provider = connection.provider
                appointment.external_calendar_event_id = external_id
                await db.commit()
        except Exception:
            logger.exception("Failed to push appointment %s to %s calendar", appointment.id, connection.provider)


async def sync_appointment_updated(db: AsyncSession, appointment) -> None:
    """Push an update to whichever calendar this appointment was originally synced to"""
    connection = await _tracked_connection(db, appointment)
    if not connection:
        return
    access_token = await _valid_access_token(db, connection)
    if not access_token:
        return
    try:
        provider = get_calendar_provider(connection.provider)
        await provider.update_event(
            access_token,
            connection.external_calendar_id,
            appointment.external_calendar_event_id,
            _to_calendar_event(appointment),
        )
    except Exception:
        logger.exception("Failed to update appointment %s on %s calendar", appointment.id, connection.provider)


async def sync_appointment_deleted(db: AsyncSession, appointment) -> None:
    """Remove this appointment from whichever calendar it was synced to.
    Must be called BEFORE the appointment row itself is deleted."""
    connection = await _tracked_connection(db, appointment)
    if not connection:
        return
    access_token = await _valid_access_token(db, connection)
    if not access_token:
        return
    try:
        provider = get_calendar_provider(connection.provider)
        await provider.delete_event(access_token, connection.external_calendar_id, appointment.external_calendar_event_id)
    except Exception:
        logger.exception("Failed to delete appointment %s on %s calendar", appointment.id, connection.provider)


async def _tracked_connection(db: AsyncSession, appointment) -> Optional[CalendarConnection]:
    if not appointment.external_calendar_provider or not appointment.external_calendar_event_id:
        return None
    connections = await _get_connections(db, appointment.user_id)
    return next((c for c in connections if c.provider == appointment.external_calendar_provider), None)
