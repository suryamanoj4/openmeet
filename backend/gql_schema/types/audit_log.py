"""AuditLog GraphQL type."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class AuditLogType:
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str
    resource_type: str
    resource_id: Optional[uuid.UUID]
    organization_id: Optional[uuid.UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    changes: Optional[JSON]
    created_at: datetime