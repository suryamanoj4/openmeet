"""GraphQL contract tests for event workflows."""

from datetime import datetime, timedelta, timezone

from gql_schema import schema
from gql_schema.datetime_utils import to_naive_utc


def test_personal_event_organization_is_nullable_in_public_schema():
    result = schema.execute_sync(
        """
        query {
          __type(name: "EventType") {
            fields {
              name
              type { kind }
            }
          }
        }
        """
    )
    organization_field = next(
        field
        for field in result.data["__type"]["fields"]
        if field["name"] == "organizationId"
    )

    assert organization_field["type"]["kind"] != "NON_NULL"


def test_current_user_organizations_can_be_filtered_by_membership_role():
    result = schema.execute_sync(
        """
        query {
          __type(name: "UserType") {
            fields {
              name
              args { name }
            }
          }
        }
        """
    )
    organizations_field = next(
        field
        for field in result.data["__type"]["fields"]
        if field["name"] == "organizations"
    )

    assert {"name": "role"} in organizations_field["args"]


def test_event_datetimes_are_normalized_for_naive_utc_database_columns():
    india_time = datetime(
        2026, 8, 1, 15, 30, tzinfo=timezone(timedelta(hours=5, minutes=30))
    )

    assert to_naive_utc(india_time) == datetime(2026, 8, 1, 10, 0)
