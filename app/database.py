"""Database configuration and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

_connect_args = {}
if "+asyncpg" in settings.database_url:
    # Supabase's connection pooler (and pgbouncer transaction pooling in
    # general) doesn't support asyncpg's server-side prepared statement
    # cache - leaving it on causes intermittent "prepared statement ...
    # already exists" errors under concurrent serverless invocations.
    # Safe to disable unconditionally; it also suits short-lived
    # serverless connections that gain little from statement caching.
    _connect_args["statement_cache_size"] = 0

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    connect_args=_connect_args,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def get_db():
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
