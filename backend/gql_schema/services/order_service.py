"""Order service for managing ticket orders."""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from strawberry import Info

from gql_schema.services.base import BaseService
from gql_schema.services.mapping import type_mapper
from models import Order, OrderItem, Ticket, Event


class OrderService(BaseService[Order]):
    """Service for order operations."""

    def generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"OM-{timestamp}-{random_part}"

    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        result = await self.session.exec(
            select(Order).where(Order.order_number == order_number)
        )
        return result.first()

    async def get_by_id(self, id: UUID) -> Optional[Order]:
        result = await self.session.exec(
            select(Order).where(Order.id == id)
        )
        return result.first()

    async def get_by_event(
        self,
        event_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        query = select(Order).where(Order.event_id == event_id)
        if status:
            query = query.where(Order.status == status)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def get_by_customer_email(
        self,
        event_id: UUID,
        email: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        query = select(Order).where(
            Order.event_id == event_id,
            Order.customer_email == email,
        )
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def create_order(
        self,
        event_id: UUID,
        customer_email: str,
        customer_name: str,
        customer_phone: Optional[str],
        items: List[dict],
        notes: Optional[str] = None,
    ) -> Order:
        """Create a new pending order with items."""
        event = await self.session.get(Event, event_id)
        if not event:
            raise ValueError("Event not found")

        order_number = self.generate_order_number()
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        subtotal = 0.0
        order_items = []

        for item_data in items:
            ticket = await self.session.get(Ticket, item_data["ticket_id"])
            if not ticket:
                raise ValueError(f"Ticket {item_data['ticket_id']} not found")
            if not ticket.is_active:
                raise ValueError(f"Ticket {ticket.name} is not available")

            quantity = item_data["quantity"]
            total_price = float(ticket.price) * quantity

            if ticket.sold_quantity + quantity > ticket.quantity:
                raise ValueError(f"Not enough tickets available for {ticket.name}")

            subtotal += total_price

            order_item = OrderItem(
                order_id=None,
                ticket_id=ticket.id,
                quantity=quantity,
                unit_price=ticket.price,
                total_price=total_price,
            )
            order_items.append(order_item)
            ticket.sold_quantity += quantity

        total_amount = subtotal
        discount_amount = 0.0
        tax_amount = 0.0

        order = Order(
            event_id=event_id,
            order_number=order_number,
            status="pending",
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            currency="USD",
            payment_status="unpaid",
            expires_at=expires_at,
            notes=notes,
        )

        self.session.add(order)
        await self.session.flush()

        for item in order_items:
            item.order_id = order.id
            self.session.add(item)

        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def confirm_order(self, order: Order) -> Order:
        """Mark order as confirmed (paid)."""
        order.status = "confirmed"
        order.payment_status = "paid"
        order.confirmed_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def cancel_order(self, order: Order, release_tickets: bool = True) -> Order:
        """Cancel order and optionally release tickets."""
        if release_tickets:
            for item in order.items:
                ticket = await self.session.get(Ticket, item.ticket_id)
                if ticket:
                    ticket.sold_quantity = max(0, ticket.sold_quantity - item.quantity)

        order.status = "cancelled"
        order.payment_status = "cancelled"
        order.cancelled_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def expire_pending_orders(self, event_id: Optional[UUID] = None) -> int:
        """Expire all pending orders older than expiry time."""
        now = datetime.utcnow()
        query = select(Order).where(
            Order.status == "pending",
            Order.expires_at <= now,
        )
        if event_id:
            query = query.where(Order.event_id == event_id)

        result = await self.session.exec(query)
        orders = list(result.all())

        count = 0
        for order in orders:
            await self.cancel_order(order, release_tickets=True)
            count += 1

        return count

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        event_id: Optional[UUID] = None,
    ) -> List[Order]:
        query = select(Order)
        if event_id:
            query = query.where(Order.event_id == event_id)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())