"""Datetime normalization at the GraphQL/database boundary."""

from datetime import datetime, timezone
from typing import Optional


def to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Convert an aware datetime to naive UTC for existing database columns."""
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
