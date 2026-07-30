"""Datetime normalization at the GraphQL/database boundary."""

from datetime import datetime, timezone
from typing import Optional


def to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Normalize to the database's naive-UTC convention.

    GraphQL inputs are expected to include an offset. Existing ORM values are
    already naive UTC, so naive values are deliberately preserved rather than
    being interpreted in the server's local timezone.
    """
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
