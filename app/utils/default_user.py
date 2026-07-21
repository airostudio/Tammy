"""Default single-tenant user for the AI assistant.

Tammy has no login/registration flow for the people the chat/telephony
interface talks to - there's one implicit business account using the
assistant. Every record the assistant creates on someone's behalf
attaches to this fixed user id so appointments/tasks/contacts satisfy
their NOT NULL user_id foreign key without requiring a real multi-user
auth system that doesn't exist yet. The admin dashboard's shared
password is a separate, unrelated mechanism for viewing this data.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

DEFAULT_USER_ID = "system"


async def ensure_default_user(db: AsyncSession) -> User:
    """Get or create the default system user that owns assistant-created records"""
    result = await db.execute(select(User).where(User.id == DEFAULT_USER_ID))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        id=DEFAULT_USER_ID,
        email="tammy@system.local",
        username="tammy-system",
        full_name="Tammy",
        hashed_password="",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
