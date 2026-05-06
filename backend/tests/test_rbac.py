"""Tests for the RBAC module — require_auth, require_role, check_event_role, require_event_role."""

import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio

from auth import AuthContext
from models import EventStaff, Event
from rbac import (
    PermissionDenied,
    require_auth,
    require_role,
    check_event_role,
    require_event_role,
    ROLE_HIERARCHY,
)


# ----- Helpers -----

def make_info(current_user=None, db_session=None):
    """Create a mock Strawberry Info object."""
    info = MagicMock()
    info.context = {"current_user": current_user, "db": db_session}
    return info


def make_auth_context(user_id=None, role="user", is_superuser=False):
    """Create a mock AuthContext."""
    ctx = MagicMock(spec=AuthContext)
    ctx.user_id = user_id or uuid.uuid4()
    ctx.role = role
    ctx.is_superuser = is_superuser
    ctx.is_authenticated = True
    return ctx


async def noop_resolver(self, info, **kwargs):
    return "success"


# =============================================================================
# PermissionDenied
# =============================================================================

class TestPermissionDenied:
    def test_default_message(self):
        exc = PermissionDenied()
        assert str(exc) == "Permission denied"

    def test_custom_message(self):
        exc = PermissionDenied("Custom error")
        assert str(exc) == "Custom error"

    def test_is_exception(self):
        assert issubclass(PermissionDenied, Exception)


# =============================================================================
# require_auth
# =============================================================================

class TestRequireAuth:
    async def test_authenticated_user_passes(self):
        auth_user = make_auth_context()
        info = make_info(current_user=auth_user)

        @require_auth
        async def resolver(self, info):
            return "ok"

        result = await resolver(None, info)
        assert result == "ok"

    async def test_unauthenticated_raises(self):
        info = make_info(current_user=None)

        @require_auth
        async def resolver(self, info):
            return "ok"

        with pytest.raises(PermissionDenied, match="Authentication required"):
            await resolver(None, info)

    async def test_bare_decorator_vs_called(self):
        auth_user = make_auth_context()
        info = make_info(current_user=auth_user)

        @require_auth
        async def bare(self, info):
            return "bare"

        @require_auth()
        async def called(self, info):
            return "called"

        assert await bare(None, info) == "bare"
        assert await called(None, info) == "called"

    async def test_info_from_kwargs(self):
        auth_user = make_auth_context()
        info = make_info(current_user=auth_user)

        @require_auth
        async def resolver(self, **kwargs):
            return "ok"

        result = await resolver(None, info=info)
        assert result == "ok"

    async def test_no_info_available_passes(self):
        @require_auth
        async def resolver(self):
            return "ok"

        result = await resolver(None)
        assert result == "ok"


# =============================================================================
# require_role
# =============================================================================

class TestRequireRole:
    async def test_admin_role_passes_for_admin(self):
        auth_user = make_auth_context(role="admin")
        info = make_info(current_user=auth_user)

        @require_role("admin")
        async def resolver(self, info):
            return "ok"

        result = await resolver(None, info)
        assert result == "ok"

    async def test_admin_role_fails_for_user(self):
        auth_user = make_auth_context(role="user")
        info = make_info(current_user=auth_user)

        @require_role("admin")
        async def resolver(self, info):
            return "ok"

        with pytest.raises(PermissionDenied, match="Requires role 'admin' or higher"):
            await resolver(None, info)

    async def test_user_role_passes_for_user(self):
        auth_user = make_auth_context(role="user")
        info = make_info(current_user=auth_user)

        @require_role("user")
        async def resolver(self, info):
            return "ok"

        result = await resolver(None, info)
        assert result == "ok"

    async def test_superuser_bypasses_all_checks(self):
        auth_user = make_auth_context(role="user", is_superuser=True)
        info = make_info(current_user=auth_user)

        @require_role("admin")
        async def resolver(self, info):
            return "ok"

        result = await resolver(None, info)
        assert result == "ok"

    async def test_unauthenticated_raises(self):
        info = make_info(current_user=None)

        @require_role("admin")
        async def resolver(self, info):
            return "ok"

        with pytest.raises(PermissionDenied, match="Authentication required"):
            await resolver(None, info)

    async def test_role_hierarchy_is_correct(self):
        assert ROLE_HIERARCHY == {"user": 0, "admin": 1}
        assert ROLE_HIERARCHY["user"] < ROLE_HIERARCHY["admin"]


# =============================================================================
# check_event_role (needs DB)
# =============================================================================

class TestCheckEventRole:
    @pytest_asyncio.fixture(scope="function")
    async def db_session(self):
        """Create a fresh in-memory SQLite session per test."""
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
        from sqlalchemy.pool import StaticPool
        from sqlmodel import SQLModel
        from sqlmodel.ext.asyncio.session import AsyncSession

        engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        session_local = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_local() as session:
            yield session

    async def test_returns_true_when_staff_exists(self, db_session):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()

        e = Event(id=event_id, name="Test", slug="test", event_type="conference",
                   start_date=datetime.utcnow() + timedelta(days=30),
                   end_date=datetime.utcnow() + timedelta(days=31))
        db_session.add(e)
        staff = EventStaff(event_id=event_id, user_id=user_id, role="organizer", is_owner=True)
        db_session.add(staff)
        await db_session.flush()

        result = await check_event_role(db_session, event_id, user_id, "organizer")
        assert result is True

    async def test_returns_false_when_no_staff(self, db_session):
        result = await check_event_role(db_session, uuid.uuid4(), uuid.uuid4(), "organizer")
        assert result is False

    async def test_returns_false_on_role_mismatch(self, db_session):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()

        e = Event(id=event_id, name="Test", slug="test", event_type="conference",
                   start_date=datetime.utcnow() + timedelta(days=30),
                   end_date=datetime.utcnow() + timedelta(days=31))
        db_session.add(e)
        staff = EventStaff(event_id=event_id, user_id=user_id, role="staff", is_owner=False)
        db_session.add(staff)
        await db_session.flush()

        result = await check_event_role(db_session, event_id, user_id, "organizer")
        assert result is False

    async def test_returns_false_when_staff_inactive(self, db_session):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()

        e = Event(id=event_id, name="Test", slug="test", event_type="conference",
                   start_date=datetime.utcnow() + timedelta(days=30),
                   end_date=datetime.utcnow() + timedelta(days=31))
        db_session.add(e)
        staff = EventStaff(event_id=event_id, user_id=user_id, role="organizer",
                            is_owner=True, is_active=False)
        db_session.add(staff)
        await db_session.flush()

        result = await check_event_role(db_session, event_id, user_id, "organizer")
        assert result is False


# =============================================================================
# require_event_role (needs DB + mock info)
# =============================================================================

class TestRequireEventRole:
    @pytest_asyncio.fixture(scope="function")
    async def db_session(self):
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
        from sqlalchemy.pool import StaticPool
        from sqlmodel import SQLModel
        from sqlmodel.ext.asyncio.session import AsyncSession

        engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        session_local = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_local() as session:
            yield session

    async def test_organizer_passes(self, db_session):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()

        e = Event(id=event_id, name="Test", slug="test", event_type="conference",
                   start_date=datetime.utcnow() + timedelta(days=30),
                   end_date=datetime.utcnow() + timedelta(days=31))
        db_session.add(e)
        db_session.add(EventStaff(event_id=event_id, user_id=user_id, role="organizer", is_owner=True))
        await db_session.flush()

        auth_user = make_auth_context(user_id=user_id, role="user")
        info = make_info(current_user=auth_user, db_session=db_session)

        result = await require_event_role(info, event_id, "organizer")
        assert result is None

    async def test_non_organizer_raises(self, db_session):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()

        e = Event(id=event_id, name="Test", slug="test", event_type="conference",
                   start_date=datetime.utcnow() + timedelta(days=30),
                   end_date=datetime.utcnow() + timedelta(days=31))
        db_session.add(e)
        await db_session.flush()

        auth_user = make_auth_context(user_id=user_id, role="user")
        info = make_info(current_user=auth_user, db_session=db_session)

        with pytest.raises(PermissionDenied, match="do not have the 'organizer' role"):
            await require_event_role(info, event_id, "organizer")

    async def test_unauthenticated_raises(self, db_session):
        info = make_info(current_user=None, db_session=db_session)

        with pytest.raises(PermissionDenied, match="Authentication required"):
            await require_event_role(info, uuid.uuid4(), "organizer")

    async def test_superuser_bypasses_check(self, db_session):
        event_id = uuid.uuid4()
        auth_user = make_auth_context(user_id=uuid.uuid4(), role="user", is_superuser=True)
        info = make_info(current_user=auth_user, db_session=db_session)

        result = await require_event_role(info, event_id, "organizer")
        assert result is None
