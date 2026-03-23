"""Attendee model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class AttendeeBase(SQLModel):
    """Base attendee fields."""

    order_item_id: uuid.UUID = Field(foreign_key="order_items.id", ondelete="CASCADE")
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", ondelete="RESTRICT")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    company: Optional[str] = Field(default=None, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=100)
    custom_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    check_in_status: str = Field(default="not_checked_in", max_length=50)
    check_in_at: Optional[datetime] = Field(default=None)
    check_in_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    notes: Optional[str] = Field(default=None)


class Attendee(AttendeeBase, table=True):
    """Attendee model (individual ticket holder)."""

    __tablename__ = "attendees"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    order_item: "OrderItem" = Relationship(back_populates="attendees")
    ticket: "Ticket" = Relationship(back_populates="attendees")

    def __repr__(self) -> str:
        return f"<Attendee {self.email}>"
