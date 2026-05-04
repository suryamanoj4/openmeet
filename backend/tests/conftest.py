"""Test fixtures and configuration.

Monkeypatches postgresql.JSONB -> JSON for SQLite compatibility.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Make JSONB work on SQLite by aliasing it to JSON
import sqlalchemy.dialects.postgresql as _pg
_pg.JSONB = JSON

from auth import hash_password  # noqa: E402
from models import (  # noqa: E402
    Event,
    Member,
    Organization,
    Ticket,
    User,
)

_counter = 0
def _next_email() -> str:
    global _counter
    _counter += 1
    return f"test{_counter}@example.com"

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def engine():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def db_session(session: AsyncSession) -> AsyncSession:
    return session


@pytest_asyncio.fixture
async def seeded_user(db_session: AsyncSession) -> User:
    user = User(
        email=_next_email(),
        password_hash=hash_password("secret123"),
        first_name="Test",
        last_name="User",
        role="user",
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def seeded_org(db_session: AsyncSession, seeded_user: User) -> Organization:
    org = Organization(
        name="Test Org",
        slug=_next_email().replace("@", "-").replace(".", "-"),
        description="A test organization",
    )
    db_session.add(org)
    await db_session.flush()

    member = Member(user_id=seeded_user.id, organization_id=org.id, role="admin")
    db_session.add(member)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def seeded_event(
    db_session: AsyncSession, seeded_org: Organization
) -> Event:
    from datetime import datetime, timedelta

    event = Event(
        organization_id=seeded_org.id,
        name="Test Event",
        slug="test-event",
        description="A test event",
        event_type="conference",
        status="published",
        visibility="public",
        start_date=datetime.utcnow() + timedelta(days=30),
        end_date=datetime.utcnow() + timedelta(days=31),
    )
    db_session.add(event)
    await db_session.flush()
    return event


@pytest_asyncio.fixture
async def seeded_ticket(
    db_session: AsyncSession, seeded_event: Event
) -> Ticket:
    ticket = Ticket(
        event_id=seeded_event.id,
        name="General Admission",
        price=1000.0,
        currency="USD",
        quantity=100,
        sort_order=0,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket
