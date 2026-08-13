"""Generate an iCalendar (.ics) feed from appointments.

The simplest possible calendar integration: no OAuth, no external
developer account, no setup beyond sharing a URL. Any calendar app
(Google Calendar, Outlook, Apple Calendar, ...) can subscribe to the
feed URL and see appointments, refreshed periodically by that app. Like
the OAuth providers, this is one-way (Tammy -> calendar) and read-only
from the calendar app's side - there's no write-back path in the iCal
subscription model.
"""

from datetime import datetime, timezone
from typing import Iterable


def _escape_ics_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _format_dt(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _fold_line(line: str) -> str:
    """RFC 5545 requires content lines longer than 75 octets to be folded"""
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(parts)


def generate_ics_feed(appointments: Iterable) -> str:
    """Build a VCALENDAR feed of VEVENTs from a list of Appointment rows"""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ENDCOM.NET AI Assistant//Calendar Feed//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    now = _format_dt(datetime.utcnow())

    for appointment in appointments:
        lines.append("BEGIN:VEVENT")
        lines.append(_fold_line(f"UID:{appointment.id}@endcom.net"))
        lines.append(f"DTSTAMP:{now}")
        lines.append(f"DTSTART:{_format_dt(appointment.start_time)}")
        lines.append(f"DTEND:{_format_dt(appointment.end_time)}")
        lines.append(_fold_line(f"SUMMARY:{_escape_ics_text(appointment.title)}"))
        if appointment.description:
            lines.append(_fold_line(f"DESCRIPTION:{_escape_ics_text(appointment.description)}"))
        if appointment.location:
            lines.append(_fold_line(f"LOCATION:{_escape_ics_text(appointment.location)}"))
        status = "CANCELLED" if appointment.status == "cancelled" else "CONFIRMED"
        lines.append(f"STATUS:{status}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
