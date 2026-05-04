"""Ticket service for managing ticket types and inventory."""

from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from strawberry import Info
from datetime import datetime

from gql_schema.services.base import BaseService
from models import Ticket, Event


class TicketService(BaseService[Ticket]):
    """Service for ticket operations."""

    async def get_by_id(self, id: UUID) -> Optional[Ticket]:
        result = await self.session.exec(
            select(Ticket).where(Ticket.id == id)
        )
        return result.first()

    async def get_by_event(
        self,
        event_id: UUID,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        query = select(Ticket).where(Ticket.event_id == event_id)
        if active_only:
            query = query.where(Ticket.is_active == True)
        query = query.order_by(Ticket.sort_order)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def get_available_tickets(
        self,
        event_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        now = datetime.utcnow()
        query = select(Ticket).where(
            Ticket.event_id == event_id,
            Ticket.is_active == True,
        )
        query = query.where(
            (Ticket.sale_start == None) | (Ticket.sale_start <= now)
        )
        query = query.where(
            (Ticket.sale_end == None) | (Ticket.sale_end >= now)
        )
        query = query.where(Ticket.quantity > Ticket.sold_quantity)
        query = query.order_by(Ticket.sort_order)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def check_availability(self, ticket_id: UUID, quantity: int) -> bool:
        """Check if requested quantity is available."""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            return False
        return (ticket.quantity - ticket.sold_quantity) >= quantity

    async def reserve_tickets(self, ticket_id: UUID, quantity: int) -> Ticket:
        """Reserve tickets (mark as sold)."""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        available = ticket.quantity - ticket.sold_quantity
        if available < quantity:
            raise ValueError(
                f"Only {available} tickets available, requested {quantity}"
            )

        ticket.sold_quantity += quantity
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def release_tickets(self, ticket_id: UUID, quantity: int) -> Ticket:
        """Release tickets (return to inventory)."""
        ticket = await self.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        ticket.sold_quantity = max(0, ticket.sold_quantity - quantity)
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def deactivate(self, ticket: Ticket) -> Ticket:
        """Deactivate a ticket type."""
        ticket.is_active = False
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        event_id: Optional[UUID] = None,
    ) -> List[Ticket]:
        query = select(Ticket)
        if event_id:
            query = query.where(Ticket.event_id == event_id)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())