"""Shared FastAPI dependencies for API routes"""

from typing import Optional

from fastapi import Cookie, Header, HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings
from app.utils.auth import decode_access_token

ADMIN_COOKIE_NAME = "tammy_admin_session"


def _verify_supabase_jwt(token: str) -> Optional[dict]:
    """Verify a Supabase Auth access token.

    Uses the project's JWT Secret (Supabase Dashboard -> Project Settings
    -> API -> JWT Settings), which signs every access token with HS256
    regardless of whether the project has also enabled the newer
    asymmetric (ES256/JWKS) signing keys - so this works for any Supabase
    project as long as SUPABASE_JWT_SECRET is set.
    """
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        return None
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError:
        return None


async def require_admin(
    tammy_admin_session: Optional[str] = Cookie(default=None),
    authorization: Optional[str] = Header(default=None),
) -> dict:
    """Require either a Supabase Auth session or the legacy admin-password
    session cookie.

    The Next.js frontend authenticates with Supabase Auth directly and
    sends the resulting session as `Authorization: Bearer <token>` - no
    cookie needed, which is what makes this work cross-origin against a
    backend deployed as a separate Vercel project. The original
    single-page admin dashboard (public/admin/) still works unchanged via
    its cookie session from POST /api/admin/login.
    """
    if authorization and authorization.lower().startswith("bearer "):
        payload = _verify_supabase_jwt(authorization[7:])
        if payload:
            return payload

    if tammy_admin_session:
        payload = decode_access_token(tammy_admin_session)
        if payload and payload.get("role") == "admin":
            return payload

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
