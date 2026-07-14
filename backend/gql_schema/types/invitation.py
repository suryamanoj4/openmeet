"""Invitation GraphQL type."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class InvitationType:
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    role: str
    status: str
    token: str
    invited_by: uuid.UUID
    accepted_by: Optional[uuid.UUID]
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime