import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class AttendeeType:
    id: uuid.UUID
    order_item_id: uuid.UUID
    ticket_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    custom_data: JSON
    check_in_status: bool
    check_in_at: Optional[datetime]
    check_in_by: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
