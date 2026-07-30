"""Unit coverage for commerce idempotency boundaries without a database."""

import uuid
from unittest.mock import AsyncMock

from sqlalchemy import UniqueConstraint

from gql_schema.services.order_service import OrderService
from gql_schema.services.payment_service import PaymentService
from models import Attendee, Order, Payment


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def first(self):
        return self.value


def order() -> Order:
    return Order(
        id=uuid.uuid4(),
        event_id=uuid.uuid4(),
        order_number="OM-20260730-TEST",
        customer_email="buyer@example.com",
        customer_name="Buyer",
        subtotal=100,
        total_amount=100,
        currency="INR",
    )


def payment(target_order: Order) -> Payment:
    return Payment(
        id=uuid.uuid4(),
        order_id=target_order.id,
        provider="razorpay",
        provider_order_id="order_123",
        provider_payment_id=None,
        amount=100,
        currency="INR",
        status="pending",
    )


async def test_payment_confirmation_is_locked_and_idempotent(monkeypatch):
    target_order = order()
    target_payment = payment(target_order)
    session = AsyncMock()
    session.exec.side_effect = [
        ScalarResult(target_payment),
        ScalarResult(target_order),
        ScalarResult(target_payment),
        ScalarResult(target_payment),
        ScalarResult(target_order),
        ScalarResult(target_payment),
    ]
    confirm = AsyncMock(return_value=target_order)
    monkeypatch.setattr(OrderService, "confirm_order", confirm)
    service = PaymentService(session)

    first = await service.mark_payment_success(
        "order_123", provider_payment_id="pay_123"
    )
    second = await service.mark_payment_success(
        "order_123", provider_payment_id="pay_123"
    )

    assert first is second is target_payment
    assert target_payment.provider_payment_id == "pay_123"
    assert target_payment.status == "completed"
    confirm.assert_awaited_once()


async def test_failed_payment_releases_the_order_once(monkeypatch):
    target_order = order()
    target_payment = payment(target_order)
    session = AsyncMock()
    session.exec.side_effect = [
        ScalarResult(target_payment),
        ScalarResult(target_order),
        ScalarResult(target_payment),
    ]
    cancel = AsyncMock(return_value=target_order)
    monkeypatch.setattr(OrderService, "cancel_order", cancel)

    failed = await PaymentService(session).mark_payment_failed(
        "order_123", failure_reason="Declined"
    )

    assert failed is target_payment
    assert failed.status == "failed"
    cancel.assert_awaited_once_with(target_order)


async def test_refund_replay_returns_existing_refund():
    target_order = order()
    target_payment = payment(target_order)
    target_payment.status = "completed"
    session = AsyncMock()
    session.exec.side_effect = [
        ScalarResult(target_payment),
        ScalarResult(target_payment),
    ]
    service = PaymentService(session)

    first = await service.process_refund("pay_123", 50)
    second = await service.process_refund("pay_123", 50)

    assert first is second is target_payment
    assert target_payment.status == "refunded"
    assert float(target_payment.refunded_amount) == 50


def test_attendee_slots_have_a_database_uniqueness_boundary():
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in Attendee.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("order_item_id", "sequence_number") in unique_columns
