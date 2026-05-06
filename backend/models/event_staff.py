"""Event staff model — links users to events as organizers."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class EventStaffBase(SQLModel):
    """Base event staff fields."""

    event_id: uuid.UUID = Field(foreign_key="events.id", ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    role: str = Field(max_length=50, default="organizer")
    is_owner: bool = Field(default=False)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")


class EventStaff(EventStaffBase, table=True):
    """Event staff/organizer assignment model."""

    __tablename__ = "event_staff"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    event: "Event" = Relationship(back_populates="staff_assignments")
    user: "User" = Relationship(
        back_populates="event_staff_assignments",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(EventStaff.user_id) == User.id",
        },
    )

    def __repr__(self) -> str:
        return f"<EventStaff {self.user_id} as {self.role}>"
