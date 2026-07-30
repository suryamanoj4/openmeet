"""Payment service for managing payment transactions."""

import uuid
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlmodel import select

from gql_schema.services.base import BaseService
from models import Payment, Order


class PaymentService(BaseService[Payment]):
    """Service for payment transaction operations."""

    async def get_by_id(self, id: UUID) -> Optional[Payment]:
        result = await self.session.exec(select(Payment).where(Payment.id == id))
        return result.first()

    async def get_by_provider_payment_id(self, provider_payment_id: str) -> Optional[Payment]:
        result = await self.session.exec(
            select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        )
        return result.first()

    async def get_by_provider_order_id(
        self, provider_order_id: str
    ) -> Optional[Payment]:
        result = await self.session.exec(
            select(Payment).where(Payment.provider_order_id == provider_order_id)
        )
        return result.first()

    async def get_pending_by_order(
        self, order_id: UUID, provider: str
    ) -> Optional[Payment]:
        result = await self.session.exec(
            select(Payment).where(
                Payment.order_id == order_id,
                Payment.provider == provider,
                Payment.status == "pending",
            )
        )
        return result.first()

    async def get_by_order(
        self,
        order_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Payment]:
        result = await self.session.exec(
            select(Payment)
            .where(Payment.order_id == order_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payment]:
        result = await self.session.exec(select(Payment).offset(skip).limit(limit))
        return list(result.all())

    async def create_payment(
        self,
        order_id: UUID,
        provider: str,
        provider_order_id: str,
        amount: float,
        currency: str,
        provider_payment_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> Payment:
        """Create a payment record (initiated by frontend)."""
        order = await self.session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")

        payment = Payment(
            order_id=order_id,
            provider=provider,
            provider_order_id=provider_order_id,
            provider_payment_id=provider_payment_id,
            amount=amount,
            currency=currency,
            status="pending",
            payment_method=payment_method,
            extra_data=extra_data or {},
        )
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def mark_payment_success(
        self,
        provider_order_id: str,
        provider_payment_id: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> Optional[Payment]:
        """Mark payment as successful (called from webhook)."""
        existing = await self.get_by_provider_order_id(provider_order_id)
        if not existing:
            return None

        order_result = await self.session.exec(
            select(Order).where(Order.id == existing.order_id).with_for_update()
        )
        order = order_result.first()
        payment_result = await self.session.exec(
            select(Payment)
            .where(Payment.id == existing.id)
            .with_for_update()
        )
        payment = payment_result.first()
        if not payment:
            return None

        if payment.status == "completed":
            if (
                provider_payment_id
                and payment.provider_payment_id
                and payment.provider_payment_id != provider_payment_id
            ):
                raise ValueError("Provider payment ID does not match")
            return payment
        if payment.status != "pending":
            raise ValueError(f"Cannot complete a {payment.status} payment")
        if (
            provider_payment_id
            and payment.provider_payment_id
            and payment.provider_payment_id != provider_payment_id
        ):
            raise ValueError("Provider payment ID does not match")
        if provider_payment_id:
            payment.provider_payment_id = provider_payment_id
        payment.status = "completed"
        if extra_data:
            payment.extra_data = {**payment.extra_data, **extra_data}

        if order:
            from gql_schema.services.order_service import OrderService

            order.payment_status = "paid"
            await OrderService(self.session).confirm_order(order)

        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def mark_payment_failed(
        self,
        provider_order_id: str,
        failure_reason: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> Optional[Payment]:
        """Mark payment as failed (called from webhook)."""
        existing = await self.get_by_provider_order_id(provider_order_id)
        if not existing:
            return None

        order_result = await self.session.exec(
            select(Order).where(Order.id == existing.order_id).with_for_update()
        )
        order = order_result.first()
        payment_result = await self.session.exec(
            select(Payment)
            .where(Payment.id == existing.id)
            .with_for_update()
        )
        payment = payment_result.first()
        if not payment:
            return None
        if payment.status == "failed":
            return payment
        if payment.status == "completed":
            raise ValueError("A completed payment cannot be marked failed")
        payment.status = "failed"
        payment.failure_reason = failure_reason
        if extra_data:
            payment.extra_data = {**payment.extra_data, **extra_data}

        if order:
            from gql_schema.services.order_service import OrderService

            await OrderService(self.session).cancel_order(order)
            order.payment_status = "failed"

        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def process_refund(
        self,
        provider_payment_id: str,
        refund_amount: float,
        refund_reason: Optional[str] = None,
    ) -> Optional[Payment]:
        """Process a refund for a payment."""
        result = await self.session.exec(
            select(Payment)
            .where(Payment.provider_payment_id == provider_payment_id)
            .with_for_update()
        )
        payment = result.first()
        if not payment:
            return None

        if payment.status == "refunded":
            return payment
        if payment.status != "completed":
            raise ValueError("Can only refund completed payments")
        if refund_amount <= 0 or refund_amount > float(payment.amount):
            raise ValueError("Refund amount must be positive and no more than the payment")

        payment.refunded_amount = float(refund_amount)
        payment.refund_reason = refund_reason
        payment.refunded_at = datetime.utcnow()
        payment.status = "refunded"

        await self.session.flush()
        await self.session.refresh(payment)
        return payment
