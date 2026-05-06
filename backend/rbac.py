"""Role-Based Access Control — pluggable decorators for resolvers.

Usage:
    @require_auth
    @require_role("admin")
    async def admin_only_mutation(self, info: Info, ...): ...

    @require_auth
    async def event_mutation(self, info: Info, event_id: UUID, ...):
        await require_event_role(info, event_id, "organizer")
        ...
"""

import uuid
from functools import wraps
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from models import EventStaff


ROLE_HIERARCHY = {"user": 0, "admin": 1}


def _get_info(args, kwargs):
    """Extract Strawberry Info from resolver arguments."""
    for a in args:
        if hasattr(a, "context"):
            return a
    return kwargs.get("info")


def _get_auth_user(info):
    """Get AuthContext from GraphQL info."""
    ctx = info.context
    if isinstance(ctx, dict):
        return ctx.get("current_user")
    return None


class PermissionDenied(Exception):
    """Raised when a user lacks required permissions."""

    def __init__(self, message: str = "Permission denied"):
        self.message = message
        super().__init__(self.message)


def require_auth(resolver_func=None, *, allow_public: bool = False):
    """Decorator: require an authenticated user.

    Can be used bare (@require_auth) or with arguments.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            info = _get_info(args, kwargs)
            if info is not None and hasattr(info, "context"):
                current_user = _get_auth_user(info)
                if current_user is None:
                    raise PermissionDenied("Authentication required")
            return await func(*args, **kwargs)

        return wrapper

    if resolver_func is not None:
        return decorator(resolver_func)
    return decorator


def require_role(role: str):
    """Decorator: require a minimum platform role.

    Hierarchy: user (0) < admin (1)
    is_superuser bypasses all checks.

    Usage:
        @require_role("admin")
        async def delete_user(self, info: Info, ...): ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            info = _get_info(args, kwargs)
            if info is not None and hasattr(info, "context"):
                current_user = _get_auth_user(info)
                if current_user is None:
                    raise PermissionDenied("Authentication required")
                if current_user.is_superuser:
                    return await func(*args, **kwargs)
                user_level = ROLE_HIERARCHY.get(current_user.role, 0)
                required_level = ROLE_HIERARCHY.get(role, 0)
                if user_level < required_level:
                    raise PermissionDenied(
                        f"Requires role '{role}' or higher"
                    )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def check_event_role(
    session: AsyncSession,
    event_id: uuid.UUID,
    user_id: uuid.UUID,
    required_role: str = "organizer",
) -> bool:
    """Low-level: check if a user has a specific role on an event.

    Returns True/False, no side effects.
    """
    result = await session.exec(
        select(EventStaff).where(
            EventStaff.event_id == event_id,
            EventStaff.user_id == user_id,
            EventStaff.role == required_role,
            EventStaff.is_active == True,
        )
    )
    return result.first() is not None


async def require_event_role(
    info,
    event_id: uuid.UUID,
    required_role: str = "organizer",
) -> None:
    """Require the current user to have a specific role on an event.

    Call this inside a resolver to check event-level permissions.
    Raises PermissionDenied if the check fails.

    Usage:
        async def update_event(self, info: Info, id: UUID, ...):
            await require_event_role(info, id, "organizer")
            ...
    """
    current_user = _get_auth_user(info)
    if current_user is None:
        raise PermissionDenied("Authentication required")

    if current_user.is_superuser:
        return

    session: AsyncSession = info.context["db"]
    has_role = await check_event_role(
        session, event_id, current_user.user_id, required_role
    )
    if not has_role:
        raise PermissionDenied(
            f"You do not have the '{required_role}' role on this event"
        )
