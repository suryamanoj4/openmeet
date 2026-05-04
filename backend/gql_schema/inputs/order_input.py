"""Order input types."""

import strawberry
from enum import Enum
from typing import Optional
from uuid import UUID


@strawberry.input
class OrderItemInput:
    ticket_id: UUID
    quantity: int


@strawberry.input
class CreateOrderInput:
    event_id: UUID
    customer_email: str
    customer_name: str
    customer_phone: Optional[str] = None
    items: list[OrderItemInput]
    notes: Optional[str] = None


@strawberry.input
class UpdateOrderInput:
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"