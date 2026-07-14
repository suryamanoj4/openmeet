"""Notification GraphQL type."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class NotificationType:
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: str
    title: str
    message: str
    data: Optional[JSON]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime