from datetime import datetime
from typing import Optional
from uuid import UUID

import strawberry
from strawberry import input


@input
class CreateTicketInput:
    event_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "USD"
    quantity: int
    min_per_order: int = 1
    max_per_order: int = 10
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None
    is_active: bool = True


@input
class UpdateTicketInput:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    quantity: Optional[int] = None
    min_per_order: Optional[int] = None
    max_per_order: Optional[int] = None
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None
    is_active: Optional[bool] = None


@strawberry.type
class TicketMutationResult:
    ticket: Optional["TicketType"]
    error: Optional[str]
