from datetime import datetime
from typing import Optional
from uuid import UUID

import strawberry
from strawberry import input
from strawberry.scalars import JSON


@input
class CreateEventInput:
    organization_id: Optional[UUID] = None
    name: str
    slug: str
    description: Optional[str] = None
    event_type: str = "conference"
    status: str = "draft"
    visibility: str = "public"
    start_date: datetime
    end_date: datetime
    timezone: str = "UTC"
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    is_online: bool = False
    online_url: Optional[str] = None
    max_attendees: Optional[int] = None
    min_tickets_per_order: int = 1
    max_tickets_per_order: int = 10
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    settings: Optional[JSON] = None


@input
class UpdateEventInput:
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    is_online: Optional[bool] = None
    online_url: Optional[str] = None
    max_attendees: Optional[int] = None
    min_tickets_per_order: Optional[int] = None
    max_tickets_per_order: Optional[int] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    settings: Optional[JSON] = None


@strawberry.type
class EventMutationResult:
    event: Optional["EventType"]
    error: Optional[str]
