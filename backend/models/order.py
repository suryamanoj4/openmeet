"""Order model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Numeric


class OrderBase(SQLModel):
    """Base order fields."""

    event_id: uuid.UUID = Field(foreign_key="events.id", ondelete="CASCADE")
    order_number: str = Field(unique=True, index=True, max_length=20)
    status: str = Field(default="pending", max_length=50)
    customer_email: str = Field(max_length=255)
    customer_name: str = Field(max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    subtotal: float = Field(sa_column=Column("subtotal", Numeric(10, 2), nullable=False))
    tax_amount: float = Field(default=0.0, sa_column=Column("tax_amount", Numeric(10, 2), nullable=False))
    discount_amount: float = Field(default=0.0, sa_column=Column("discount_amount", Numeric(10, 2), nullable=False))
    total_amount: float = Field(sa_column=Column("total_amount", Numeric(10, 2), nullable=False))
    currency: str = Field(default="USD", max_length=3)
    payment_status: str = Field(default="unpaid", max_length=50)
    notes: Optional[str] = Field(default=None)
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    expires_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)


class Order(OrderBase, table=True):
    """Customer order model (ticket purchases)."""

    __tablename__ = "orders"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Relationships
    event: "Event" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    payments: list["Payment"] = Relationship(back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    attendees: list["Attendee"] = Relationship(back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self) -> str:
        return f"<Order {self.order_number}>"
