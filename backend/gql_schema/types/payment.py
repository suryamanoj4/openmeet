import uuid
from datetime import datetime
from typing import Optional

import strawberry
from strawberry.scalars import JSON


@strawberry.type
class PaymentType:
    id: uuid.UUID
    order_id: uuid.UUID
    provider: str
    provider_order_id: str
    provider_payment_id: Optional[str]
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    extra_data: Optional[JSON]
    failure_reason: Optional[str]
    refunded_amount: float
    refund_reason: Optional[str]
    refunded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool
