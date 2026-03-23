"""Database connection and session management."""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings


# Sync engine (for migrations)
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", ""),
    echo=settings.debug,
    future=True,
)

# Async engine (for application)
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """Dependency for getting sync database session."""
    with Session(sync_engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
