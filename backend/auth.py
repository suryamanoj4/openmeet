"""Authentication and authorization utilities."""

import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from config import settings
from models import EventStaff, RefreshToken, User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: uuid.UUID, role: str, is_superuser: bool) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "is_superuser": is_superuser,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token_str(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def store_refresh_token(
    session: AsyncSession,
    user_id: uuid.UUID,
    token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> RefreshToken:
    payload = decode_token(token)
    expires_at = datetime.utcfromtimestamp(payload["exp"]) if payload else datetime.utcnow()

    rt = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(token),
        expires_at=expires_at,
        created_ip=ip_address,
        user_agent=user_agent,
    )
    session.add(rt)
    await session.flush()
    return rt


async def verify_refresh_token(session: AsyncSession, token: str) -> Optional[RefreshToken]:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return None

    token_hash = _hash_token(token)
    result = await session.exec(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow(),
        )
    )
    return result.first()


async def revoke_refresh_token(session: AsyncSession, token: str) -> bool:
    token_hash = _hash_token(token)
    result = await session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    rt = result.first()
    if rt:
        rt.revoked = True
        rt.revoked_at = datetime.utcnow()
        await session.flush()
        return True
    return False


async def revoke_all_user_tokens(session: AsyncSession, user_id: uuid.UUID) -> int:
    result = await session.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
        )
    )
    tokens = list(result.all())
    for rt in tokens:
        rt.revoked = True
        rt.revoked_at = datetime.utcnow()
    await session.flush()
    return len(tokens)


async def get_current_user(session: AsyncSession, token: str) -> Optional[User]:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    result = await session.exec(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.first()
    if not user or not user.is_active:
        return None

    return user


class AuthContext:
    """Holds the authenticated user for the current request."""

    def __init__(self, user: User, token_payload: dict):
        self.user = user
        self.user_id = user.id
        self.role = user.role
        self.is_superuser = user.is_superuser
        self.token_payload = token_payload

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None


def require_auth(resolver_func=None, *, allow_public: bool = False):
    """Decorator to require authentication on a resolver."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            info = None
            for a in args:
                if hasattr(a, "context"):
                    info = a
                    break
            if info is None:
                info = kwargs.get("info")

            if info is not None and hasattr(info, "context"):
                ctx = info.context
                if isinstance(ctx, dict):
                    current_user = ctx.get("current_user")
                    if current_user is None:
                        raise PermissionError("Authentication required")

            return await func(*args, **kwargs)

        return wrapper

    if resolver_func is not None:
        return decorator(resolver_func)
    return decorator


def require_role(role: str):
    """Decorator to require a minimum platform role.

    Hierarchy: user (0) < admin (1)
    is_superuser bypasses all checks.
    """

    ROLE_HIERARCHY = {"user": 0, "admin": 1}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            info = None
            for a in args:
                if hasattr(a, "context"):
                    info = a
                    break
            if info is None:
                info = kwargs.get("info")

            if info is not None and hasattr(info, "context"):
                ctx = info.context
                if isinstance(ctx, dict):
                    current_user = ctx.get("current_user")
                    if current_user is None:
                        raise PermissionError("Authentication required")
                    if current_user.is_superuser:
                        return await func(*args, **kwargs)
                    user_level = ROLE_HIERARCHY.get(current_user.role, 0)
                    required_level = ROLE_HIERARCHY.get(role, 0)
                    if user_level < required_level:
                        raise PermissionError(f"Requires role '{role}' or higher")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def check_event_role(
    session: AsyncSession,
    event_id: uuid.UUID,
    user_id: uuid.UUID,
    required_role: str = "organizer",
) -> bool:
    """Check if a user has a specific role on an event."""
    result = await session.exec(
        select(EventStaff).where(
            EventStaff.event_id == event_id,
            EventStaff.user_id == user_id,
            EventStaff.role == required_role,
            EventStaff.is_active == True,
        )
    )
    return result.first() is not None


async def get_auth_context(
    session: AsyncSession,
    authorization: Optional[str] = None,
) -> Optional[AuthContext]:
    """Extract auth context from Authorization header."""
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    user = await get_current_user(session, token)
    if not user:
        return None

    payload = decode_token(token)
    return AuthContext(user=user, token_payload=payload or {})
