"""Ticket model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, CheckConstraint, Numeric


class TicketBase(SQLModel):
    """Base ticket fields."""

    event_id: uuid.UUID = Field(foreign_key="events.id", ondelete="CASCADE")
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    price: float = Field(sa_column=Column("price", Numeric(10, 2), nullable=False))
    currency: str = Field(default="USD", max_length=3)
    quantity: int = Field(default=0)
    sold_quantity: int = Field(default=0)
    min_per_order: int = Field(default=1)
    max_per_order: int = Field(default=10)
    sale_start: Optional[datetime] = Field(default=None)
    sale_end: Optional[datetime] = Field(default=None)
    sort_order: int = Field(default=0)


class Ticket(TicketBase, table=True):
    """Ticket type model."""

    __tablename__ = "tickets"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    event: "Event" = Relationship(back_populates="tickets")
    order_items: list["OrderItem"] = Relationship(back_populates="ticket")
    attendees: list["Attendee"] = Relationship(back_populates="ticket")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="chk_tickets_quantity"),
        CheckConstraint("sold_quantity <= quantity", name="chk_tickets_sold_quantity"),
        CheckConstraint("price >= 0", name="chk_tickets_price"),
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.name}>"
