"""Tests for explicit production administrator bootstrapping."""

import uuid

import pytest

from auth import verify_password
from bootstrap_admin import (
    AdminConfig,
    BootstrapAdminError,
    config_from_environment,
    create_admin,
)
from models import User


def admin_config(email: str | None = None) -> AdminConfig:
    return AdminConfig(
        email=email or f"admin-{uuid.uuid4()}@example.com",
        password="a-strong-admin-password",
        first_name="Platform",
        last_name="Administrator",
    )


def test_environment_configuration_is_validated_and_normalized():
    config = config_from_environment(
        {
            "ADMIN_EMAIL": " Admin@Example.COM ",
            "ADMIN_PASSWORD": "a-strong-admin-password",
        }
    )

    assert config.email == "Admin@example.com"
    assert config.first_name == "Platform"
    assert config.last_name == "Administrator"


@pytest.mark.parametrize(
    ("environment", "message"),
    [
        ({"ADMIN_PASSWORD": "a-strong-admin-password"}, "ADMIN_EMAIL is required"),
        (
            {
                "ADMIN_EMAIL": "not-an-email",
                "ADMIN_PASSWORD": "a-strong-admin-password",
            },
            "ADMIN_EMAIL is invalid",
        ),
        (
            {"ADMIN_EMAIL": "admin@example.com", "ADMIN_PASSWORD": "too-short"},
            "at least 12 characters",
        ),
    ],
)
def test_environment_configuration_rejects_unsafe_input(environment, message):
    with pytest.raises(BootstrapAdminError, match=message):
        config_from_environment(environment)


async def test_create_admin_is_privileged_verified_and_idempotent(db_session):
    config = admin_config()

    user, created = await create_admin(db_session, config)
    repeated_user, repeated_created = await create_admin(db_session, config)

    assert created is True
    assert repeated_created is False
    assert repeated_user.id == user.id
    assert user.role == "admin"
    assert user.is_superuser is True
    assert user.is_email_verified is True
    assert verify_password(config.password, user.password_hash)


async def test_create_admin_refuses_to_elevate_an_existing_user(db_session):
    config = admin_config()
    db_session.add(
        User(
            email=config.email,
            password_hash="not-used",
            first_name="Ordinary",
            last_name="User",
            role="user",
            is_superuser=False,
        )
    )
    await db_session.flush()

    with pytest.raises(BootstrapAdminError, match="refusing automatic privilege"):
        await create_admin(db_session, config)
