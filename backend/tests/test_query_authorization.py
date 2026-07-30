"""Behavior tests for the GraphQL authorization boundary."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from gql_schema import schema
from gql_schema.inputs import CreateUserInput
from gql_schema.mutations import Mutation, require_order_owner_or_admin
from gql_schema.queries import Query, require_authenticated, require_platform_admin
from gql_schema.services.event_service import EventService
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


@pytest.mark.asyncio
async def test_create_user_requires_platform_admin():
    with pytest.raises(PermissionDenied, match="Requires role 'admin'"):
        await Mutation().create_user(
            info_for(user()),
            CreateUserInput(email="blocked@example.com", password="secret123"),
        )


@pytest.mark.asyncio
async def test_management_queries_reject_anonymous_access():
    query = Query()

    with pytest.raises(PermissionDenied, match="Authentication required"):
        await query.organization(info_for(), uuid4())
    with pytest.raises(PermissionDenied, match="Authentication required"):
        await query.organization_by_slug(info_for(), "private-org")
    with pytest.raises(PermissionDenied, match="Authentication required"):
        await query.event_by_slug(info_for(), uuid4(), "private-event")


@pytest.mark.asyncio
async def test_organization_list_requires_platform_admin():
    with pytest.raises(PermissionDenied, match="administrator"):
        await Query().organizations(info_for(user()))


def test_attendees_query_exposes_a_real_event_filter():
    result = schema.execute_sync(
        """
        query {
          __type(name: "Query") {
            fields {
              name
              args { name }
            }
          }
        }
        """
    )
    attendees = next(
        field for field in result.data["__type"]["fields"]
        if field["name"] == "attendees"
    )

    assert {"name": "eventId"} in attendees["args"]
    assert {"name": "ticketId"} in attendees["args"]


def test_order_access_allows_owner_and_platform_admin_only():
    owner = user()
    order = SimpleNamespace(created_by=owner.user_id)

    assert require_order_owner_or_admin(info_for(owner), order) is owner

    admin = user(role="admin")
    assert require_order_owner_or_admin(info_for(admin), order) is admin

    with pytest.raises(PermissionDenied, match="own this order"):
        require_order_owner_or_admin(info_for(user()), order)


@pytest.mark.asyncio
async def test_event_service_uses_graphql_permission_error(monkeypatch):
    service = EventService(None)

    async def is_not_organizer(*_args):
        return False

    monkeypatch.setattr(service, "user_is_organizer", is_not_organizer)

    with pytest.raises(PermissionDenied, match="not an organizer"):
        await service.ensure_organizer(uuid4(), uuid4())
