"""Payment provider GraphQL types."""

import uuid

import strawberry


@strawberry.type
class PaymentOrderPayload:
    provider_order_id: str
    provider_key_id: str
    order_id: uuid.UUID
    order_number: str
    amount: int
    currency: str


@strawberry.type
class PaymentVerificationResult:
    success: bool
    order_id: uuid.UUID
    payment_status: str
    message: str
