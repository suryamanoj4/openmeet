"""Order service for managing ticket orders."""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import func
from sqlmodel import select

from gql_schema.services.base import BaseService
from models import Attendee, Order, OrderItem, Ticket, Event


class OrderService(BaseService[Order]):
    """Service for order operations."""

    def generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_part = uuid.uuid4().hex[:10].upper()
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

    async def get_by_id_for_update(self, id: UUID) -> Optional[Order]:
        result = await self.session.exec(
            select(Order).where(Order.id == id).with_for_update()
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

    async def get_by_creator(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        result = await self.session.exec(
            select(Order)
            .where(Order.created_by == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    async def create_order(
        self,
        event_id: UUID,
        customer_email: str,
        customer_name: str,
        customer_phone: Optional[str],
        items: List[dict],
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> Order:
        """Create a new pending order with items."""
        event_result = await self.session.exec(
            select(Event).where(Event.id == event_id).with_for_update()
        )
        event = event_result.first()
        now = datetime.utcnow()
        if not event or not event.is_active:
            raise ValueError("Event not found")
        if event.status != "published":
            raise ValueError("Only published events can accept orders")
        if event.end_date <= now:
            raise ValueError("This event has already ended")
        if event.registration_start and event.registration_start > now:
            raise ValueError("Registration has not opened")
        if event.registration_end and event.registration_end < now:
            raise ValueError("Registration has closed")

        order_number = self.generate_order_number()
        expires_at = now + timedelta(minutes=15)

        subtotal = 0.0
        order_items = []

        currencies: set[str] = set()
        requested_quantity = sum(item["quantity"] for item in items)
        if event.max_attendees is not None:
            sold_result = await self.session.exec(
                select(func.coalesce(func.sum(Ticket.sold_quantity), 0)).where(
                    Ticket.event_id == event_id,
                )
            )
            reserved = int(sold_result.one())
            if reserved + requested_quantity > event.max_attendees:
                raise ValueError("Event capacity is no longer available")

        for item_data in sorted(items, key=lambda item: str(item["ticket_id"])):
            ticket_result = await self.session.exec(
                select(Ticket)
                .where(Ticket.id == item_data["ticket_id"])
                .with_for_update()
            )
            ticket = ticket_result.first()
            if not ticket:
                raise ValueError(f"Ticket {item_data['ticket_id']} not found")
            if ticket.event_id != event_id:
                raise ValueError(f"Ticket {ticket.name} does not belong to this event")
            if not ticket.is_active:
                raise ValueError(f"Ticket {ticket.name} is not available")

            quantity = item_data["quantity"]
            if quantity < ticket.min_per_order or quantity > ticket.max_per_order:
                raise ValueError(
                    f"{ticket.name} requires between {ticket.min_per_order} "
                    f"and {ticket.max_per_order} tickets per order"
                )
            if ticket.sale_start and ticket.sale_start > now:
                raise ValueError(f"Sales have not opened for {ticket.name}")
            if ticket.sale_end and ticket.sale_end < now:
                raise ValueError(f"Sales have closed for {ticket.name}")
            total_price = float(ticket.price) * quantity

            if ticket.sold_quantity + quantity > ticket.quantity:
                raise ValueError(f"Not enough tickets available for {ticket.name}")

            subtotal += total_price
            currencies.add(ticket.currency)

            order_item = OrderItem(
                order_id=None,
                ticket_id=ticket.id,
                quantity=quantity,
                unit_price=ticket.price,
                total_price=total_price,
            )
            order_items.append(order_item)
            ticket.sold_quantity += quantity

        if len(currencies) != 1:
            raise ValueError("All tickets in an order must use the same currency")

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
            currency=currencies.pop(),
            payment_status="unpaid",
            expires_at=expires_at,
            notes=notes,
            created_by=created_by,
        )

        self.session.add(order)
        await self.session.flush()

        for item in order_items:
            item.order_id = order.id
            self.session.add(item)

        await self.session.flush()
        if total_amount == 0:
            await self.confirm_order(order)
        await self.session.refresh(order)
        return order

    async def confirm_order(self, order: Order) -> Order:
        """Mark order as confirmed (paid)."""
        locked_result = await self.session.exec(
            select(Order).where(Order.id == order.id).with_for_update()
        )
        order = locked_result.first()
        if not order:
            raise ValueError("Order not found")
        if order.status == "confirmed":
            return order
        if order.status != "pending":
            raise ValueError(f"Cannot confirm an order with status {order.status}")
        order.status = "confirmed"
        order.payment_status = "paid" if float(order.total_amount) > 0 else "free"
        order.confirmed_at = datetime.utcnow()
        await self.session.flush()
        await self._create_attendees(order)
        await self.session.refresh(order)
        return order

    async def _create_attendees(self, order: Order) -> None:
        item_result = await self.session.exec(
            select(OrderItem)
            .where(OrderItem.order_id == order.id)
            .order_by(OrderItem.id)
        )
        name_parts = order.customer_name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else "Guest"
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        for item in item_result.all():
            existing_result = await self.session.exec(
                select(Attendee.sequence_number).where(
                    Attendee.order_item_id == item.id
                )
            )
            existing_sequences = set(existing_result.all())
            for sequence_number in range(item.quantity):
                if sequence_number in existing_sequences:
                    continue
                self.session.add(
                    Attendee(
                        order_item_id=item.id,
                        ticket_id=item.ticket_id,
                        sequence_number=sequence_number,
                        first_name=first_name,
                        last_name=last_name,
                        email=order.customer_email,
                        phone=order.customer_phone,
                    )
                )
        await self.session.flush()

    async def cancel_order(self, order: Order, release_tickets: bool = True) -> Order:
        """Cancel order and optionally release tickets."""
        if order.status == "cancelled":
            return order
        if order.status != "pending":
            raise ValueError(f"Cannot cancel an order with status {order.status}")
        if release_tickets:
            item_result = await self.session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            for item in sorted(item_result.all(), key=lambda value: str(value.ticket_id)):
                ticket_result = await self.session.exec(
                    select(Ticket)
                    .where(Ticket.id == item.ticket_id)
                    .with_for_update()
                )
                ticket = ticket_result.first()
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
