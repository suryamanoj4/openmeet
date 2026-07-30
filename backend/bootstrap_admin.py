"""Explicitly create the first production administrator.

This command is intentionally separate from application startup and demo
seeding. It never promotes an existing non-superuser account or changes an
existing administrator's password.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Mapping

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import hash_password
from database import AsyncSessionLocal
from models import User


MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_BYTES = 72


class BootstrapAdminError(ValueError):
    """Raised when administrator bootstrap input or state is unsafe."""


@dataclass(frozen=True)
class AdminConfig:
    email: str
    password: str
    first_name: str
    last_name: str


def config_from_environment(environment: Mapping[str, str]) -> AdminConfig:
    """Validate administrator settings supplied through environment variables."""
    raw_email = environment.get("ADMIN_EMAIL", "").strip()
    password = environment.get("ADMIN_PASSWORD", "")
    first_name = environment.get("ADMIN_FIRST_NAME", "Platform").strip()
    last_name = environment.get("ADMIN_LAST_NAME", "Administrator").strip()

    if not raw_email:
        raise BootstrapAdminError("ADMIN_EMAIL is required")
    try:
        email = validate_email(
            raw_email,
            check_deliverability=False,
        ).normalized
    except EmailNotValidError as exc:
        raise BootstrapAdminError(f"ADMIN_EMAIL is invalid: {exc}") from exc

    if len(password) < MIN_PASSWORD_LENGTH:
        raise BootstrapAdminError(
            f"ADMIN_PASSWORD must contain at least {MIN_PASSWORD_LENGTH} characters"
        )
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise BootstrapAdminError(
            f"ADMIN_PASSWORD must not exceed {MAX_PASSWORD_BYTES} UTF-8 bytes"
        )
    if not first_name or len(first_name) > 100:
        raise BootstrapAdminError(
            "ADMIN_FIRST_NAME must contain between 1 and 100 characters"
        )
    if not last_name or len(last_name) > 100:
        raise BootstrapAdminError(
            "ADMIN_LAST_NAME must contain between 1 and 100 characters"
        )

    return AdminConfig(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


async def create_admin(session: AsyncSession, config: AdminConfig) -> tuple[User, bool]:
    """Create a superuser, returning ``(user, created)``.

    An existing superuser makes the operation idempotent. An existing ordinary
    account is never silently elevated.
    """
    result = await session.exec(
        select(User).where(func.lower(User.email) == config.email.lower())
    )
    existing = result.first()
    if existing is not None:
        if existing.role == "admin" and existing.is_superuser:
            return existing, False
        raise BootstrapAdminError(
            "ADMIN_EMAIL already belongs to a non-superuser account; "
            "refusing automatic privilege escalation"
        )

    user = User(
        email=config.email,
        password_hash=hash_password(config.password),
        first_name=config.first_name,
        last_name=config.last_name,
        role="admin",
        is_superuser=True,
        is_email_verified=True,
    )
    session.add(user)
    await session.flush()
    return user, True


async def bootstrap_from_environment(
    environment: Mapping[str, str] = os.environ,
) -> None:
    config = config_from_environment(environment)
    async with AsyncSessionLocal() as session:
        user, created = await create_admin(session, config)
        await session.commit()

    action = "Created" if created else "Already configured"
    print(f"{action} production administrator: {user.email}")


if __name__ == "__main__":
    try:
        asyncio.run(bootstrap_from_environment())
    except BootstrapAdminError as exc:
        raise SystemExit(f"Administrator bootstrap failed: {exc}") from exc
