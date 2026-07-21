"""Admin session endpoints - login/logout for the shared admin password"""

import hmac

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.api.deps import ADMIN_COOKIE_NAME, require_admin
from app.config import get_settings
from app.utils.auth import create_access_token

router = APIRouter()


class AdminLoginRequest(BaseModel):
    password: str


@router.post("/login")
async def admin_login(payload: AdminLoginRequest, response: Response):
    """Exchange the shared admin password for a session cookie"""
    settings = get_settings()

    if not settings.admin_password:
        raise HTTPException(status_code=503, detail="Admin access is not configured")

    if not hmac.compare_digest(payload.password, settings.admin_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"role": "admin"})
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return {"status": "ok"}


@router.post("/logout")
async def admin_logout(response: Response):
    """Clear the admin session cookie"""
    response.delete_cookie(ADMIN_COOKIE_NAME, path="/")
    return {"status": "ok"}


@router.get("/me")
async def admin_me(_admin: dict = Depends(require_admin)):
    """Check whether the current request has a valid admin session"""
    return {"authenticated": True}
