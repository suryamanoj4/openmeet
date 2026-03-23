"""Order item model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, CheckConstraint, Numeric


class OrderItemBase(SQLModel):
    """Base order item fields."""

    order_id: uuid.UUID = Field(foreign_key="orders.id", ondelete="CASCADE")
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", ondelete="RESTRICT")
    quantity: int
    unit_price: float = Field(sa_column=Column("unit_price", Numeric(10, 2), nullable=False))
    total_price: float = Field(sa_column=Column("total_price", Numeric(10, 2), nullable=False))


class OrderItem(OrderItemBase, table=True):
    """Order item model (individual ticket items within an order)."""

    __tablename__ = "order_items"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    order: "Order" = Relationship(back_populates="items")
    ticket: "Ticket" = Relationship(back_populates="order_items")
    attendees: list["Attendee"] = Relationship(back_populates="order_item")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_order_items_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_order_items_unit_price"),
    )

    def __repr__(self) -> str:
        return f"<OrderItem {self.id}>"
