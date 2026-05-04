"""GraphQL Mutation definitions."""

from typing import Optional
from uuid import UUID

import strawberry
from strawberry import Info
from passlib.hash import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession

from gql_schema.types import (
    UserType,
    OrganizationType,
    EventType,
    TicketType,
    OrderType,
    AttendeeType,
)
from gql_schema.inputs import (
    CreateUserInput,
    UpdateUserInput,
    CreateOrganizationInput,
    UpdateOrganizationInput,
    CreateEventInput,
    UpdateEventInput,
    CreateTicketInput,
    UpdateTicketInput,
    CreateOrderInput,
    UpdateOrderInput,
    OrderItemInput,
)
from gql_schema.services import (
    UserService,
    OrganizationService,
    EventService,
    TicketService,
    OrderService,
    AttendeeService,
)
from gql_schema.services.mapping import (
    user_to_type,
    organization_to_type,
    event_to_type,
    ticket_to_type,
    order_to_type,
    attendee_to_type,
)
from models import User, Organization, Event, Ticket


def get_session(info: Info) -> AsyncSession:
    return info.context["db"]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self,
        info: Info,
        input: CreateUserInput,
    ) -> UserType:
        session = get_session(info)
        service = UserService(session)
        user = await service.create(
            User,
            email=input.email,
            password_hash=bcrypt.hash(input.password),
            first_name=input.first_name,
            last_name=input.last_name,
            phone=input.phone,
            avatar_url=input.avatar_url,
        )
        await session.commit()
        return UserType(**user_to_type(user))

    @strawberry.mutation
    async def update_user(
        self,
        info: Info,
        id: UUID,
        input: UpdateUserInput,
    ) -> Optional[UserType]:
        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_id(id)
        if not user:
            return None

        update_data = {}
        if input.first_name is not None:
            update_data["first_name"] = input.first_name
        if input.last_name is not None:
            update_data["last_name"] = input.last_name
        if input.phone is not None:
            update_data["phone"] = input.phone
        if input.avatar_url is not None:
            update_data["avatar_url"] = input.avatar_url

        user = await service.update(user, **update_data)
        await session.commit()
        return UserType(**user_to_type(user))

    @strawberry.mutation
    async def delete_user(
        self,
        info: Info,
        id: UUID,
    ) -> bool:
        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_id(id)
        if not user:
            return False
        await service.delete(user)
        await session.commit()
        return True

    @strawberry.mutation
    async def create_organization(
        self,
        info: Info,
        input: CreateOrganizationInput,
    ) -> OrganizationType:
        session = get_session(info)
        service = OrganizationService(session)
        org = await service.create(
            Organization,
            name=input.name,
            slug=input.slug,
            description=input.description,
            logo_url=input.logo_url,
            website_url=input.website_url,
            social_links=input.social_links,
            settings=input.settings,
        )
        await session.commit()
        return OrganizationType(**organization_to_type(org))

    @strawberry.mutation
    async def update_organization(
        self,
        info: Info,
        id: UUID,
        input: UpdateOrganizationInput,
    ) -> Optional[OrganizationType]:
        session = get_session(info)
        service = OrganizationService(session)
        org = await service.get_by_id(id)
        if not org:
            return None

        update_data = {}
        if input.name is not None:
            update_data["name"] = input.name
        if input.description is not None:
            update_data["description"] = input.description
        if input.logo_url is not None:
            update_data["logo_url"] = input.logo_url
        if input.website_url is not None:
            update_data["website_url"] = input.website_url
        if input.social_links is not None:
            update_data["social_links"] = input.social_links
        if input.settings is not None:
            update_data["settings"] = input.settings

        org = await service.update(org, **update_data)
        await session.commit()
        return OrganizationType(**organization_to_type(org))

    @strawberry.mutation
    async def delete_organization(
        self,
        info: Info,
        id: UUID,
    ) -> bool:
        session = get_session(info)
        service = OrganizationService(session)
        org = await service.get_by_id(id)
        if not org:
            return False
        await service.delete(org)
        await session.commit()
        return True

    @strawberry.mutation
    async def add_organization_member(
        self,
        info: Info,
        organization_id: UUID,
        user_id: UUID,
        role: str = "member",
    ) -> bool:
        session = get_session(info)
        service = OrganizationService(session)
        try:
            await service.add_member(organization_id, user_id, role)
            await session.commit()
            return True
        except ValueError:
            return False

    @strawberry.mutation
    async def remove_organization_member(
        self,
        info: Info,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        session = get_session(info)
        service = OrganizationService(session)
        result = await service.remove_member(organization_id, user_id)
        await session.commit()
        return result

    @strawberry.mutation
    async def follow_organization(
        self,
        info: Info,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        session = get_session(info)
        service = OrganizationService(session)
        await service.add_follower(organization_id, user_id)
        await session.commit()
        return True

    @strawberry.mutation
    async def unfollow_organization(
        self,
        info: Info,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        session = get_session(info)
        service = OrganizationService(session)
        return await service.remove_follower(organization_id, user_id)

    @strawberry.mutation
    async def create_event(
        self,
        info: Info,
        input: CreateEventInput,
    ) -> EventType:
        session = get_session(info)
        service = EventService(session)
        event = await service.create(
            Event,
            organization_id=input.organization_id,
            name=input.name,
            slug=input.slug,
            description=input.description,
            event_type=input.event_type,
            status=input.status,
            visibility=input.visibility,
            start_date=input.start_date,
            end_date=input.end_date,
            timezone=input.timezone,
            venue_name=input.venue_name,
            venue_address=input.venue_address,
            venue_city=input.venue_city,
            venue_country=input.venue_country,
            is_online=input.is_online,
            online_url=input.online_url,
            max_attendees=input.max_attendees,
            min_tickets_per_order=input.min_tickets_per_order,
            max_tickets_per_order=input.max_tickets_per_order,
            registration_start=input.registration_start,
            registration_end=input.registration_end,
            cover_image_url=input.cover_image_url,
            banner_image_url=input.banner_image_url,
            settings=input.settings,
        )
        await session.commit()
        return EventType(**event_to_type(event))

    @strawberry.mutation
    async def update_event(
        self,
        info: Info,
        id: UUID,
        input: UpdateEventInput,
    ) -> Optional[EventType]:
        session = get_session(info)
        service = EventService(session)
        event = await service.get_by_id(id)
        if not event:
            return None

        update_data = {k: v for k, v in input.__dict__.items() if v is not None}
        event = await service.update(event, **update_data)
        await session.commit()
        return EventType(**event_to_type(event))

    @strawberry.mutation
    async def delete_event(
        self,
        info: Info,
        id: UUID,
    ) -> bool:
        session = get_session(info)
        service = EventService(session)
        event = await service.get_by_id(id)
        if not event:
            return False
        await service.delete(event)
        await session.commit()
        return True

    @strawberry.mutation
    async def create_ticket(
        self,
        info: Info,
        input: CreateTicketInput,
    ) -> TicketType:
        session = get_session(info)
        service = TicketService(session)
        ticket = await service.create(
            Ticket,
            event_id=input.event_id,
            name=input.name,
            description=input.description,
            price=input.price,
            currency=input.currency,
            quantity=input.quantity,
            min_per_order=input.min_per_order,
            max_per_order=input.max_per_order,
            sale_start=input.sale_start,
            sale_end=input.sale_end,
            sort_order=input.sort_order,
        )
        await session.commit()
        return TicketType(**ticket_to_type(ticket))

    @strawberry.mutation
    async def update_ticket(
        self,
        info: Info,
        id: UUID,
        input: UpdateTicketInput,
    ) -> Optional[TicketType]:
        session = get_session(info)
        service = TicketService(session)
        ticket = await service.get_by_id(id)
        if not ticket:
            return None

        update_data = {k: v for k, v in input.__dict__.items() if v is not None}
        ticket = await service.update(ticket, **update_data)
        await session.commit()
        return TicketType(**ticket_to_type(ticket))

    @strawberry.mutation
    async def delete_ticket(
        self,
        info: Info,
        id: UUID,
    ) -> bool:
        session = get_session(info)
        service = TicketService(session)
        ticket = await service.get_by_id(id)
        if not ticket:
            return False
        await service.deactivate(ticket)
        await session.commit()
        return True

    @strawberry.mutation
    async def create_order(
        self,
        info: Info,
        input: CreateOrderInput,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        try:
            items = [{"ticket_id": item.ticket_id, "quantity": item.quantity} for item in input.items]
            order = await service.create_order(
                event_id=input.event_id,
                customer_email=input.customer_email,
                customer_name=input.customer_name,
                customer_phone=input.customer_phone,
                items=items,
                notes=input.notes,
            )
            await session.commit()
            return OrderType(**order_to_type(order))
        except ValueError:
            await session.rollback()
            return None

    @strawberry.mutation
    async def confirm_order(
        self,
        info: Info,
        id: UUID,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        order = await service.get_by_id(id)
        if not order:
            return None
        order = await service.confirm_order(order)
        await session.commit()
        return OrderType(**order_to_type(order))

    @strawberry.mutation
    async def cancel_order(
        self,
        info: Info,
        id: UUID,
        release_tickets: bool = True,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        order = await service.get_by_id(id)
        if not order:
            return None
        order = await service.cancel_order(order, release_tickets=release_tickets)
        await session.commit()
        return OrderType(**order_to_type(order))

    @strawberry.mutation
    async def check_in_attendee(
        self,
        info: Info,
        attendee_id: UUID,
        checked_in_by: UUID,
    ) -> Optional[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        try:
            attendee = await service.check_in(attendee_id, checked_in_by)
            await session.commit()
            return AttendeeType(**attendee_to_type(attendee))
        except ValueError:
            await session.rollback()
            return None

    @strawberry.mutation
    async def undo_attendee_check_in(
        self,
        info: Info,
        attendee_id: UUID,
    ) -> Optional[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        try:
            attendee = await service.undo_check_in(attendee_id)
            await session.commit()
            return AttendeeType(**attendee_to_type(attendee))
        except ValueError:
            await session.rollback()
            return None

    @strawberry.mutation
    async def update_attendee_notes(
        self,
        info: Info,
        attendee_id: UUID,
        notes: str,
    ) -> Optional[AttendeeType]:
        session = get_session(info)
        service = AttendeeService(session)
        try:
            attendee = await service.update_notes(attendee_id, notes)
            await session.commit()
            return AttendeeType(**attendee_to_type(attendee))
        except ValueError:
            await session.rollback()
            return None