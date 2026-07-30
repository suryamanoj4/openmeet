"""Behavior tests for the GraphQL authorization boundary."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from gql_schema.queries import require_authenticated, require_platform_admin
from rbac import PermissionDenied


def info_for(user=None):
    return SimpleNamespace(context={"current_user": user, "db": None})


def user(role="user", is_superuser=False):
    return SimpleNamespace(
        user_id=uuid4(),
        role=role,
        is_superuser=is_superuser,
    )


def test_anonymous_management_access_is_rejected():
    with pytest.raises(PermissionDenied, match="Authentication required"):
        require_authenticated(info_for())


def test_regular_user_cannot_read_platform_management_data():
    with pytest.raises(PermissionDenied, match="administrator"):
        require_platform_admin(info_for(user()))


def test_platform_admin_and_superuser_can_cross_management_boundary():
    admin = user(role="admin")
    superuser = user(is_superuser=True)

    assert require_platform_admin(info_for(admin)) is admin
    assert require_platform_admin(info_for(superuser)) is superuser
