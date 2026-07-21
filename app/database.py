"""Database configuration and session management"""

from sqlalchemy import inspect, text
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


# Columns added to existing models after their table may already exist in a
# live database. Base.metadata.create_all() only creates missing TABLES, it
# never alters existing ones, so a new column here needs to be added by hand
# until this project has real Alembic migrations (tracked as a known gap).
_PENDING_COLUMN_UPGRADES = {
    "appointments": [
        ("external_calendar_provider", "VARCHAR"),
        ("external_calendar_event_id", "VARCHAR"),
    ],
}


def _add_missing_columns(sync_conn):
    inspector = inspect(sync_conn)
    existing_tables = set(inspector.get_table_names())

    for table_name, columns in _PENDING_COLUMN_UPGRADES.items():
        if table_name not in existing_tables:
            continue  # create_all() will create it with every current column
        existing_columns = {c["name"] for c in inspector.get_columns(table_name)}
        for column_name, column_type in columns:
            if column_name not in existing_columns:
                sync_conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_add_missing_columns)


async def close_db():
    """Close database connections"""
    await engine.dispose()
