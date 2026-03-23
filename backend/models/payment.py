"""Payment model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Numeric


class PaymentBase(SQLModel):
    """Base payment fields."""

    order_id: uuid.UUID = Field(foreign_key="orders.id", ondelete="CASCADE")
    provider: str = Field(max_length=50)
    provider_payment_id: str = Field(unique=True, index=True, max_length=255)
    amount: float = Field(sa_column=Column("amount", Numeric(10, 2), nullable=False))
    currency: str = Field(max_length=3)
    status: str = Field(max_length=50)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    failure_reason: Optional[str] = Field(default=None)
    refunded_amount: float = Field(default=0.0, sa_column=Column("refunded_amount", Numeric(10, 2), nullable=False))
    refund_reason: Optional[str] = Field(default=None)
    refunded_at: Optional[datetime] = Field(default=None)


class Payment(PaymentBase, table=True):
    """Payment transaction model."""

    __tablename__ = "payments"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    order: "Order" = Relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment {self.provider_payment_id}>"
