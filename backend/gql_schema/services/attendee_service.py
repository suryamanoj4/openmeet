"""Attendee service for managing event attendees."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlmodel import select
from strawberry import Info

from gql_schema.services.base import BaseService
from models import Attendee, OrderItem, Ticket


class AttendeeService(BaseService[Attendee]):
    """Service for attendee operations."""

    async def get_by_id(self, id: UUID) -> Optional[Attendee]:
        result = await self.session.exec(
            select(Attendee).where(Attendee.id == id)
        )
        return result.first()

    async def get_by_order_item(self, order_item_id: UUID) -> List[Attendee]:
        result = await self.session.exec(
            select(Attendee).where(
                Attendee.order_item_id == order_item_id,
                Attendee.is_active == True,
            )
        )
        return list(result.all())

    async def get_by_ticket(
        self,
        ticket_id: UUID,
        check_in_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Attendee]:
        query = select(Attendee).where(
            Attendee.ticket_id == ticket_id,
            Attendee.is_active == True,
        )
        if check_in_status:
            query = query.where(Attendee.check_in_status == check_in_status)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def search(
        self,
        event_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Attendee]:
        search_pattern = f"%{query}%"
        stmt = (
            select(Attendee)
            .join(OrderItem)
            .join(Ticket)
            .where(Ticket.event_id == event_id)
            .where(Attendee.is_active == True)
            .where(
                (Attendee.email.ilike(search_pattern))
                | (Attendee.first_name.ilike(search_pattern))
                | (Attendee.last_name.ilike(search_pattern))
                | (Attendee.company.ilike(search_pattern))
            )
        )
        result = await self.session.exec(stmt.offset(skip).limit(limit))
        return list(result.all())

    async def check_in(
        self,
        attendee_id: UUID,
        checked_in_by: UUID,
    ) -> Attendee:
        """Check in an attendee."""
        attendee = await self.get_by_id(attendee_id)
        if not attendee:
            raise ValueError("Attendee not found")

        if attendee.check_in_status == "checked_in":
            raise ValueError("Already checked in")

        attendee.check_in_status = "checked_in"
        attendee.check_in_at = datetime.utcnow()
        attendee.check_in_by = checked_in_by
        await self.session.flush()
        await self.session.refresh(attendee)
        return attendee

    async def undo_check_in(self, attendee_id: UUID) -> Attendee:
        """Undo check-in."""
        attendee = await self.get_by_id(attendee_id)
        if not attendee:
            raise ValueError("Attendee not found")

        attendee.check_in_status = "not_checked_in"
        attendee.check_in_at = None
        attendee.check_in_by = None
        await self.session.flush()
        await self.session.refresh(attendee)
        return attendee

    async def update_notes(
        self,
        attendee_id: UUID,
        notes: str,
    ) -> Attendee:
        """Update attendee notes."""
        attendee = await self.get_by_id(attendee_id)
        if not attendee:
            raise ValueError("Attendee not found")

        attendee.notes = notes
        await self.session.flush()
        await self.session.refresh(attendee)
        return attendee

    async def get_check_in_stats(self, ticket_id: UUID) -> dict:
        """Get check-in statistics for a ticket."""
        result = await self.session.exec(
            select(Attendee).where(
                Attendee.ticket_id == ticket_id,
                Attendee.is_active == True,
            )
        )
        attendees = list(result.all())
        total = len(attendees)
        checked_in = sum(1 for a in attendees if a.check_in_status == "checked_in")

        return {
            "total": total,
            "checked_in": checked_in,
            "not_checked_in": total - checked_in,
            "check_in_rate": checked_in / total if total > 0 else 0,
        }

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        ticket_id: Optional[UUID] = None,
    ) -> List[Attendee]:
        query = select(Attendee).where(Attendee.is_active == True)
        if ticket_id:
            query = query.where(Attendee.ticket_id == ticket_id)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())