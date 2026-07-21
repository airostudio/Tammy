"""Shared FastAPI dependencies for API routes"""

from typing import Optional

from fastapi import Cookie, HTTPException, status

from app.utils.auth import decode_access_token

ADMIN_COOKIE_NAME = "tammy_admin_session"


async def require_admin(tammy_admin_session: Optional[str] = Cookie(default=None)) -> dict:
    """Require a valid admin session cookie, issued by POST /api/admin/login"""
    if not tammy_admin_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(tammy_admin_session)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    return payload
