import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class EventType:
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    event_type: str
    status: str
    visibility: str
    start_date: datetime
    end_date: datetime
    timezone: str
    venue_name: Optional[str]
    venue_address: Optional[JSON]
    venue_city: Optional[str]
    venue_country: Optional[str]
    is_online: bool
    online_url: Optional[str]
    max_attendees: Optional[int]
    min_tickets_per_order: int
    max_tickets_per_order: int
    registration_start: Optional[datetime]
    registration_end: Optional[datetime]
    cover_image_url: Optional[str]
    banner_image_url: Optional[str]
    settings: Optional[JSON]
    created_at: datetime
    updated_at: datetime
