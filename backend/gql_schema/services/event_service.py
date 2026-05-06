"""Event service for managing events."""

from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import check_event_role
from gql_schema.services.base import BaseService
from models import Event, Ticket, EventStaff, Order, User


class EventService(BaseService[Event]):
    """Service for event operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_slug(self, slug: str) -> Optional[Event]:
        result = await self.session.exec(select(Event).where(Event.slug == slug))
        return result.first()

    async def get_by_id(self, id: UUID) -> Optional[Event]:
        result = await self.session.exec(select(Event).where(Event.id == id))
        return result.first()

    async def get_tickets(self, event_id: UUID) -> List[Ticket]:
        result = await self.session.exec(
            select(Ticket)
            .where(Ticket.event_id == event_id)
            .where(Ticket.is_active == True)
        )
        return list(result.all())

    async def get_staff(self, event_id: UUID) -> List[EventStaff]:
        result = await self.session.exec(
            select(EventStaff)
            .where(EventStaff.event_id == event_id)
            .where(EventStaff.is_active == True)
        )
        return list(result.all())

    async def get_orders(self, event_id: UUID) -> List[Order]:
        result = await self.session.exec(
            select(Order)
            .where(Order.event_id == event_id)
            .where(Order.is_active == True)
        )
        return list(result.all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[UUID] = None,
    ) -> List[Event]:
        query = select(Event)
        if organization_id:
            query = query.where(Event.organization_id == organization_id)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def user_is_organizer(self, event_id: UUID, user_id: UUID) -> bool:
        return await check_event_role(self.session, event_id, user_id, "organizer")

    async def ensure_organizer(self, event_id: UUID, user_id: UUID) -> None:
        if not await self.user_is_organizer(event_id, user_id):
            raise PermissionError("You are not an organizer of this event")

    async def add_organizer(
        self, event_id: UUID, user_id: UUID, assigned_by: UUID, is_owner: bool = False
    ) -> EventStaff:
        staff = EventStaff(
            event_id=event_id,
            user_id=user_id,
            role="organizer",
            is_owner=is_owner,
            assigned_by=assigned_by,
        )
        self.session.add(staff)
        await self.session.flush()
        return staff
