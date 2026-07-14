"""EmailLog GraphQL type."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class EmailLogType:
    id: uuid.UUID
    recipient_email: str
    template_name: Optional[str]
    status: str
    error_message: Optional[str]
    extra_data: Optional[JSON]
    created_at: datetime