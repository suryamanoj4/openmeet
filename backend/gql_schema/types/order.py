import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class OrderType:
    id: uuid.UUID
    event_id: uuid.UUID
    order_number: str
    status: str
    customer_email: str
    customer_name: str
    customer_phone: Optional[str]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    currency: str
    payment_status: str
    notes: Optional[str]
    extra_data: Optional[JSON]
    expires_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime