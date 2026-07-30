"""Backend-owned validation for event scheduling and public page content."""

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class EventScheduleSchema(BaseModel):
    """Date invariants shared by create, update, and publish operations."""

    model_config = ConfigDict(extra="forbid")

    start_date: datetime
    end_date: datetime
    timezone_name: str = "UTC"
    registration_start: datetime | None = None
    registration_end: datetime | None = None

    @field_validator("timezone_name")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("must be a valid IANA timezone") from exc
        return value

    @model_validator(mode="after")
    def ordered_dates(self) -> "EventScheduleSchema":
        start = _aware_utc(self.start_date)
        end = _aware_utc(self.end_date)
        if end <= start:
            raise ValueError("end date must be after start date")

        registration_start = (
            _aware_utc(self.registration_start) if self.registration_start else None
        )
        registration_end = (
            _aware_utc(self.registration_end) if self.registration_end else None
        )
        if registration_start and registration_end and registration_end <= registration_start:
            raise ValueError("registration end must be after registration start")
        if registration_start and registration_start > start:
            raise ValueError("registration start must not be after the event starts")
        if registration_end and registration_end > end:
            raise ValueError("registration end must not be after the event ends")
        return self


class NewEventScheduleSchema(EventScheduleSchema):
    """Scheduling rules for a new or still-draft event."""

    @model_validator(mode="after")
    def starts_in_future(self) -> "NewEventScheduleSchema":
        now = datetime.now(timezone.utc)
        if _aware_utc(self.start_date) <= now:
            raise ValueError("start date must be in the future")
        if self.registration_start and _aware_utc(self.registration_start) <= now:
            raise ValueError("registration start must be in the future")
        return self


class PublishableEventScheduleSchema(EventScheduleSchema):
    """Scheduling rules for publishing a new or legacy ongoing event."""

    @model_validator(mode="after")
    def has_not_ended(self) -> "PublishableEventScheduleSchema":
        if _aware_utc(self.end_date) <= datetime.now(timezone.utc):
            raise ValueError("an event that has already ended cannot be published")
        return self


_PUBLISHABLE_BLOCK_TYPES = {
    "hero",
    "text",
    "image",
    "about",
    "schedule",
    "speakers",
    "venue",
    "faqs",
    "cta",
    "video",
    "divider",
}


def validate_publishable_blocks(blocks: list[dict[str, Any]]) -> None:
    """Reject block payloads that would require rendering arbitrary HTML."""

    for block in blocks:
        block_type = block.get("type")
        props = block.get("props") or {}
        if block_type not in _PUBLISHABLE_BLOCK_TYPES:
            raise ValueError(f"block type '{block_type}' cannot be published")
        if block_type == "venue" and props.get("mapEmbed"):
            raise ValueError("map embed HTML is not supported; use an address instead")
        if block_type == "video" and props.get("embedCode"):
            raise ValueError("video embed HTML is not supported; use a video URL instead")
