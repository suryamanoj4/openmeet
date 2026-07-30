"""GraphQL contract tests for event workflows."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from gql_schema import schema
from gql_schema.datetime_utils import to_naive_utc
from gql_schema.validation import (
    NewEventScheduleSchema,
    PublishableEventScheduleSchema,
    validate_publishable_blocks,
)


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
    naive_utc = datetime(2026, 8, 1, 10, 0)
    assert to_naive_utc(naive_utc) is naive_utc
    assert to_naive_utc(None) is None


def test_new_event_schedule_requires_a_future_start_and_later_end():
    now = datetime.now(timezone.utc)

    with pytest.raises(ValidationError, match="start date must be in the future"):
        NewEventScheduleSchema(
            start_date=now - timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            timezone_name="UTC",
        )


def test_registration_window_must_be_future_ordered_and_open_before_event():
    now = datetime.now(timezone.utc)
    start = now + timedelta(days=2)

    with pytest.raises(ValidationError, match="registration start must be in the future"):
        NewEventScheduleSchema(
            start_date=start,
            end_date=start + timedelta(hours=2),
            timezone_name="UTC",
            registration_start=now - timedelta(minutes=1),
        )

    with pytest.raises(ValidationError, match="must not be after the event starts"):
        NewEventScheduleSchema(
            start_date=start,
            end_date=start + timedelta(hours=2),
            timezone_name="UTC",
            registration_start=start + timedelta(minutes=1),
        )

    with pytest.raises(ValidationError, match="end date must be after start date"):
        NewEventScheduleSchema(
            start_date=now + timedelta(hours=2),
            end_date=now + timedelta(hours=1),
            timezone_name="UTC",
        )


def test_ongoing_legacy_event_can_publish_but_ended_event_cannot():
    now = datetime.now(timezone.utc)
    valid = PublishableEventScheduleSchema(
        start_date=now - timedelta(hours=1),
        end_date=now + timedelta(hours=1),
        timezone_name="UTC",
    )
    assert valid.end_date > valid.start_date

    with pytest.raises(ValidationError, match="already ended"):
        PublishableEventScheduleSchema(
            start_date=now - timedelta(hours=2),
            end_date=now - timedelta(hours=1),
            timezone_name="UTC",
        )


def test_publishing_rejects_arbitrary_html_and_embed_code():
    with pytest.raises(ValueError, match="cannot be published"):
        validate_publishable_blocks(
            [{"id": "unsafe", "type": "html", "visible": True, "props": {}}]
        )

    with pytest.raises(ValueError, match="video embed HTML"):
        validate_publishable_blocks(
            [
                {
                    "id": "unsafe-video",
                    "type": "video",
                    "visible": True,
                    "props": {"embedCode": "<script>alert(1)</script>"},
                }
            ]
        )

    with pytest.raises(ValueError, match="map embed HTML"):
        validate_publishable_blocks(
            [
                {
                    "id": "unsafe-map",
                    "type": "venue",
                    "visible": True,
                    "props": {"mapEmbed": "<iframe src='untrusted'></iframe>"},
                }
            ]
        )
