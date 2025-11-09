"""Helper utility functions"""

import uuid
from datetime import datetime
from typing import Optional
import pytz


def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


def parse_datetime(date_str: str, timezone: str = "UTC") -> Optional[datetime]:
    """Parse datetime string to datetime object"""
    try:
        # Try common datetime formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d",
        ]

        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue

        if dt:
            # Localize to specified timezone
            tz = pytz.timezone(timezone)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            return dt

        return None
    except Exception:
        return None


def format_datetime(dt: datetime, timezone: str = "UTC", format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    try:
        tz = pytz.timezone(timezone)
        dt_tz = dt.astimezone(tz)
        return dt_tz.strftime(format_str)
    except Exception:
        return dt.strftime(format_str)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to remove dangerous characters"""
    import re

    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    filename = re.sub(r"[^\w\-.]", "_", filename)

    # Remove multiple consecutive underscores
    filename = re.sub(r"_+", "_", filename)

    return filename


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Basic phone number validation"""
    import re

    # Remove common formatting characters
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)

    # Check if it's a valid phone number (10-15 digits)
    return bool(re.match(r"^\d{10,15}$", cleaned))
