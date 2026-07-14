"""EventPage GraphQL type (custom page builder blocks)."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class EventPageType:
    id: uuid.UUID
    event_id: uuid.UUID
    blocks: Optional[JSON]
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime