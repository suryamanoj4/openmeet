"""GraphQL Query definitions."""

from typing import List, Optional
from uuid import UUID
import strawberry
from strawberry import Info

from sqlalchemy.ext.asyncio import AsyncSession

from gql_schema.types import (
    UserType,
    OrganizationType,
    EventType,
    MemberType,
    TicketType,
    OrderType,
    AttendeeType,
    FollowerType,
    EventStaffType,
    PaymentType,
    OrderItemType,
)
from gql_schema.services import (
    UserService,
    OrganizationService,
    EventService,
    TicketService,
    OrderService,
    AttendeeService,
    PaymentService,
)
from gql_schema.services.mapping import (
    user_to_type,
    organization_to_type,
    event_to_type,
    ticket_to_type,
    order_to_type,
    order_item_to_type,
    attendee_to_type,
    payment_to_type,
    member_to_type,
    follower_to_type,
    event_staff_to_type,
)


def get_session(info: Info) -> AsyncSession:
    return info.context["db"]


def get_auth_user(info: Info):
    ctx = info.context
    if isinstance(ctx, dict) and ctx.get("current_user"):
        return ctx["current_user"]
    return None


@strawberry.type
class Query:
    @strawberry.field
    async def me(
        self,
        info: Info,
    ) -> Optional[UserType]:
        auth_user = get_auth_user(info)
        if not auth_user:
            return None

        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_id(auth_user.user_id)
        if not user:
            return None
        return UserType(**user_to_type(user))
    @strawberry.field
    async def users(
        self,
        info: Info,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserType]:
        session = get_session(info)
        service = UserService(session)
        users = await service.get_all(skip=skip, limit=limit)
        return [UserType(**user_to_type(user)) for user in users]

    @strawberry.field
    async def user(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[UserType]:
        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_id(id)
        if not user:
            return None
        return UserType(**user_to_type(user))

    @strawberry.field
    async def organizations(
        self,
        info: Info,
        skip: int = 0,
        limit: int = 100,
    ) -> List[OrganizationType]:
        session = get_session(info)
        service = OrganizationService(session)
        orgs = await service.get_all(skip=skip, limit=limit)
        return [OrganizationType(**organization_to_type(org)) for org in orgs]

    @strawberry.field
    async def organization(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[OrganizationType]:
        session = get_session(info)
        service = OrganizationService(session)
        org = await service.get_by_id(id)
        if not org:
            return None
        return OrganizationType(**organization_to_type(org))

    @strawberry.field
    async def organization_by_slug(
        self,
        info: Info,
        slug: str,
    ) -> Optional[OrganizationType]:
        session = get_session(info)
        service = OrganizationService(session)
        org = await service.get_by_slug(slug)
        if not org:
            return None
        return OrganizationType(**organization_to_type(org))

    @strawberry.field
    async def organization_members(
        self,
        info: Info,
        organization_id: UUID,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MemberType]:
        session = get_session(info)
        service = OrganizationService(session)
        members = await service.get_members(
            organization_id, role=role, skip=skip, limit=limit
        )
        return [MemberType(**member_to_type(m)) for m in members]

    @strawberry.field
    async def organization_followers(
        self,
        info: Info,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FollowerType]:
        session = get_session(info)
        service = OrganizationService(session)
        followers = await service.get_followers(
            organization_id, skip=skip, limit=limit
        )
        return [FollowerType(**follower_to_type(f)) for f in followers]

    @strawberry.field
    async def events(
        self,
        info: Info,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[EventType]:
        session = get_session(info)
        service = EventService(session)
        events = await service.get_all(
            skip=skip, limit=limit, organization_id=organization_id
        )
        return [EventType(**event_to_type(e)) for e in events]

    @strawberry.field
    async def event(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[EventType]:
        session = get_session(info)
        service = EventService(session)
        event = await service.get_by_id(id)
        if not event:
            return None
        return EventType(**event_to_type(event))

    @strawberry.field
    async def event_by_slug(
        self,
        info: Info,
        organization_id: UUID,
        slug: str,
    ) -> Optional[EventType]:
        session = get_session(info)
        service = EventService(session)
        event = await service.get_by_slug(slug)
        if not event or event.organization_id != organization_id:
            return None
        return EventType(**event_to_type(event))

    @strawberry.field
    async def event_tickets(
        self,
        info: Info,
        event_id: UUID,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TicketType]:
        session = get_session(info)
        service = TicketService(session)
        tickets = await service.get_by_event(
            event_id, active_only=active_only, skip=skip, limit=limit
        )
        return [TicketType(**ticket_to_type(t)) for t in tickets]

    @strawberry.field
    async def available_tickets(
        self,
        info: Info,
        event_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TicketType]:
        session = get_session(info)
        service = TicketService(session)
        tickets = await service.get_available_tickets(
            event_id, skip=skip, limit=limit
        )
        return [TicketType(**ticket_to_type(t)) for t in tickets]

    @strawberry.field
    async def orders(
        self,
        info: Info,
        event_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        orders = await service.get_all(
            skip=skip, limit=limit, event_id=event_id
        )
        return [OrderType(**order_to_type(o)) for o in orders]

    @strawberry.field
    async def order(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        order = await service.get_by_id(id)
        if not order:
            return None
        return OrderType(**order_to_type(order))

    @strawberry.field
    async def order_by_number(
        self,
        info: Info,
        order_number: str,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        order = await service.get_by_order_number(order_number)
        if not order:
            return None
        return OrderType(**order_to_type(order))

    @strawberry.field
    async def attendees(
        self,
        info: Info,
        ticket_id: Optional[UUID] = None,
        check_in_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        attendees = await service.get_all(
            skip=skip, limit=limit, ticket_id=ticket_id
        )
        return [AttendeeType(**attendee_to_type(a)) for a in attendees]

    @strawberry.field
    async def attendee(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        attendee = await service.get_by_id(id)
        if not attendee:
            return None
        return AttendeeType(**attendee_to_type(attendee))

    @strawberry.field
    async def search_attendees(
        self,
        info: Info,
        event_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        attendees = await service.search(event_id, query, skip=skip, limit=limit)
        return [AttendeeType(**attendee_to_type(a)) for a in attendees]

    @strawberry.field
    async def payments(
        self,
        info: Info,
        order_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[PaymentType]:
        session = get_session(info)
        service = PaymentService(session)
        if order_id:
            payments = await service.get_by_order(order_id, skip=skip, limit=limit)
        else:
            payments = await service.get_all(skip=skip, limit=limit)
        return [PaymentType(**payment_to_type(p)) for p in payments]

    @strawberry.field
    async def payment(
        self,
        info: Info,
        id: Optional[UUID] = None,
        provider_payment_id: Optional[str] = None,
    ) -> Optional[PaymentType]:
        session = get_session(info)
        service = PaymentService(session)
        if id:
            payment = await service.get_by_id(id)
        elif provider_payment_id:
            payment = await service.get_by_provider_payment_id(provider_payment_id)
        else:
            return None
        if not payment:
            return None
        return PaymentType(**payment_to_type(payment))


schema = strawberry.Schema(query=Query)