"""Event model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Index


class EventBase(SQLModel):
    """Base event fields."""

    organization_id: uuid.UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    name: str = Field(max_length=255)
    slug: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    event_type: str = Field(max_length=50)
    status: str = Field(default="draft", max_length=50)
    visibility: str = Field(default="public", max_length=50)
    start_date: datetime
    end_date: datetime
    timezone: str = Field(default="UTC", max_length=50)
    venue_name: Optional[str] = Field(default=None, max_length=255)
    venue_address: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    is_online: bool = Field(default=False)
    online_url: Optional[str] = Field(default=None, max_length=500)
    max_attendees: Optional[int] = Field(default=None)
    registration_open_date: Optional[datetime] = Field(default=None)
    registration_close_date: Optional[datetime] = Field(default=None)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)
    banner_image_url: Optional[str] = Field(default=None, max_length=500)
    settings: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class Event(EventBase, table=True):
    """Event model."""

    __tablename__ = "events"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Relationships
    organization: "Organization" = Relationship(back_populates="events")
    staff_assignments: list["EventStaff"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    tickets: list["Ticket"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    orders: list["Order"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self) -> str:
        return f"<Event {self.slug}>"
