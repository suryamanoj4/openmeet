import uuid
from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class EventStaffType:
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    is_owner: bool
    assigned_at: datetime
    assigned_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    is_active: bool
