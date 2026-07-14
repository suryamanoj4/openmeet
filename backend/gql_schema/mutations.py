"""GraphQL Mutation definitions."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import strawberry
from strawberry import Info

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token_str,
    store_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
)
from config import settings
from email_service import send_password_reset_email, send_email_verification_email, send_invitation_email
from rbac import require_auth, require_role, PermissionDenied
from payment_provider import get_provider
from gql_schema.types import (
    UserType,
    OrganizationType,
    EventType,
    TicketType,
    OrderType,
    AttendeeType,
    PaymentType,
    EventStaffType,
    AuditLogType,
    EmailLogType,
    InvitationType,
    NotificationType,
    EventPageType,
)
from gql_schema.types.auth import AuthPayload, RefreshPayload
from gql_schema.types.payment_provider import PaymentOrderPayload, PaymentVerificationResult
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
    OrderItemInput,
    UpdateEventPageInput,
)
from gql_schema.inputs.auth_input import (
    LoginInput,
    RegisterInput,
    PasswordResetRequestInput,
    PasswordResetConfirmInput,
    EmailVerificationInput,
)
from gql_schema.services import (
    UserService,
    OrganizationService,
    EventService,
    TicketService,
    OrderService,
    AttendeeService,
    PaymentService,
    NotificationService,
    EventPageService,
)
from gql_schema.services.mapping import (
    user_to_type,
    organization_to_type,
    event_to_type,
    ticket_to_type,
    order_to_type,
    attendee_to_type,
    payment_to_type,
    event_staff_to_type,
    audit_log_to_type,
    email_log_to_type,
    invitation_to_type,
    notification_to_type,
    event_page_to_type,
)
from models import User, Organization, Event, Ticket, EventStaff, AuditLog, EmailLog, Invitation, Notification, EventPage


def get_session(info: Info) -> AsyncSession:
    return info.context["db"]


def get_auth_user(info: Info):
    ctx = info.context
    if isinstance(ctx, dict) and ctx.get("current_user"):
        return ctx["current_user"]
    return None


@strawberry.type
class Mutation:
    # ================================================================
    # Auth mutations
    # ================================================================

    @strawberry.mutation
    async def register(
        self,
        info: Info,
        input: RegisterInput,
    ) -> AuthPayload:
        session = get_session(info)
        service = UserService(session)

        existing = await service.get_by_email(input.email)
        if existing:
            raise ValueError("Email already registered")

        user = await service.create(
            User,
            email=input.email,
            password_hash=hash_password(input.password),
            first_name=input.first_name or "",
            last_name=input.last_name or "",
            phone=input.phone,
        )
        await session.commit()

        access_token = create_access_token(user.id, user.role, user.is_superuser)
        refresh_token = create_refresh_token_str(user.id)
        await store_refresh_token(session, user.id, refresh_token)
        await session.commit()

        return AuthPayload(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            role=user.role,
            is_superuser=user.is_superuser,
        )

    @strawberry.mutation
    async def login(
        self,
        info: Info,
        input: LoginInput,
    ) -> AuthPayload:
        session = get_session(info)
        service = UserService(session)

        user = await service.get_by_email(input.email)
        if not user or not verify_password(input.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        access_token = create_access_token(user.id, user.role, user.is_superuser)
        refresh_token = create_refresh_token_str(user.id)
        await store_refresh_token(session, user.id, refresh_token)
        await session.commit()

        return AuthPayload(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            role=user.role,
            is_superuser=user.is_superuser,
        )

    @strawberry.mutation
    async def refresh_token(
        self,
        info: Info,
        refresh_token: str,
    ) -> RefreshPayload:
        session = get_session(info)

        rt = await verify_refresh_token(session, refresh_token)
        if not rt:
            raise ValueError("Invalid or expired refresh token")

        user = await session.get(User, rt.user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token(user.id, user.role, user.is_superuser)
        return RefreshPayload(access_token=access_token)

    @strawberry.mutation
    async def revoke_token(
        self,
        info: Info,
        refresh_token: str,
    ) -> bool:
        session = get_session(info)
        result = await revoke_refresh_token(session, refresh_token)
        await session.commit()
        return result

    @strawberry.mutation
    async def logout(
        self,
        info: Info,
        refresh_token: str,
    ) -> bool:
        session = get_session(info)
        result = await revoke_refresh_token(session, refresh_token)
        await session.commit()
        return result

    @strawberry.mutation
    @require_auth
    async def logout_all(
        self,
        info: Info,
    ) -> bool:
        auth_user = get_auth_user(info)
        session = get_session(info)
        await revoke_all_user_tokens(session, auth_user.user_id)
        await session.commit()
        return True

    @strawberry.mutation
    async def request_password_reset(
        self,
        info: Info,
        input: PasswordResetRequestInput,
    ) -> bool:
        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_email(input.email)

        if user:
            token = create_password_reset_token(user.id, user.email)
            reset_url = f"{settings.frontend_url}/auth/reset-password?token={token}"
            await send_password_reset_email(session, user.email, reset_url, user.first_name or "")
            await session.commit()
        return True

    @strawberry.mutation
    async def confirm_password_reset(
        self,
        info: Info,
        input: PasswordResetConfirmInput,
    ) -> bool:
        session = get_session(info)
        payload = verify_password_reset_token(input.token)
        if not payload:
            raise ValueError("Invalid or expired reset token")

        user_id = uuid.UUID(payload["sub"])
        user = await session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        user.password_hash = hash_password(input.new_password)
        await revoke_all_user_tokens(session, user_id)
        await session.commit()
        return True

    @strawberry.mutation
    @require_auth
    async def send_email_verification(
        self,
        info: Info,
    ) -> bool:
        auth_user = get_auth_user(info)
        session = get_session(info)
        user = await session.get(User, auth_user.user_id)

        if not user:
            raise ValueError("User not found")
        if user.is_email_verified:
            raise ValueError("Email already verified")

        token = create_email_verification_token(user.id, user.email)
        verify_url = f"{settings.frontend_url}/auth/verify-email?token={token}"
        await send_email_verification_email(session, user.email, verify_url, user.first_name or "")
        await session.commit()
        return True

    @strawberry.mutation
    async def verify_email(
        self,
        info: Info,
        input: EmailVerificationInput,
    ) -> bool:
        session = get_session(info)
        payload = verify_email_verification_token(input.token)
        if not payload:
            raise ValueError("Invalid or expired verification token")

        user_id = uuid.UUID(payload["sub"])
        user = await session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        user.is_email_verified = True
        await session.commit()
        return True

    # ================================================================
    # User mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
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
            password_hash=hash_password(input.password),
            first_name=input.first_name,
            last_name=input.last_name,
            phone=input.phone,
            avatar_url=input.avatar_url,
        )
        await session.commit()
        return UserType(**user_to_type(user))

    @strawberry.mutation
    @require_auth
    async def update_user(
        self,
        info: Info,
        id: uuid.UUID,
        input: UpdateUserInput,
    ) -> Optional[UserType]:
        auth_user = get_auth_user(info)
        session = get_session(info)
        service = UserService(session)

        if auth_user.user_id != id and not auth_user.is_superuser:
            raise PermissionDenied("You can only update your own profile")

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
    @require_auth
    @require_role("admin")
    async def delete_user(
        self,
        info: Info,
        id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        service = UserService(session)
        user = await service.get_by_id(id)
        if not user:
            return False
        await service.delete(user)
        await session.commit()
        return True

    # ================================================================
    # Organization mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def create_organization(
        self,
        info: Info,
        input: CreateOrganizationInput,
    ) -> OrganizationType:
        session = get_session(info)
        auth_user = get_auth_user(info)
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
        await service.add_member(org.id, auth_user.user_id, "admin")
        await session.commit()
        return OrganizationType(**organization_to_type(org))

    @strawberry.mutation
    @require_auth
    async def update_organization(
        self,
        info: Info,
        id: uuid.UUID,
        input: UpdateOrganizationInput,
    ) -> Optional[OrganizationType]:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = OrganizationService(session)

        member = await service.get_member(id, auth_user.user_id)
        if not member or member.role != "admin":
            raise PermissionDenied("Only org admins can update the organization")

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
    @require_auth
    async def delete_organization(
        self,
        info: Info,
        id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = OrganizationService(session)

        member = await service.get_member(id, auth_user.user_id)
        if not member or member.role != "admin":
            raise PermissionDenied("Only org admins can delete the organization")

        org = await service.get_by_id(id)
        if not org:
            return False
        await service.delete(org)
        await session.commit()
        return True

    @strawberry.mutation
    @require_auth
    async def add_organization_member(
        self,
        info: Info,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = OrganizationService(session)

        member = await service.get_member(organization_id, auth_user.user_id)
        if not member or member.role != "admin":
            raise PermissionDenied("Only org admins can add members")

        try:
            await service.add_member(organization_id, user_id, role)
            await session.commit()
            return True
        except ValueError:
            return False

    @strawberry.mutation
    @require_auth
    async def remove_organization_member(
        self,
        info: Info,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = OrganizationService(session)

        member = await service.get_member(organization_id, auth_user.user_id)
        if not member or member.role != "admin":
            raise PermissionDenied("Only org admins can remove members")

        result = await service.remove_member(organization_id, user_id)
        await session.commit()
        return result

    @strawberry.mutation
    @require_auth
    async def follow_organization(
        self,
        info: Info,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        if auth_user.user_id != user_id and not auth_user.is_superuser:
            raise PermissionDenied("You can only follow on your own behalf")
        service = OrganizationService(session)
        await service.add_follower(organization_id, user_id)
        await session.commit()
        return True

    @strawberry.mutation
    @require_auth
    async def unfollow_organization(
        self,
        info: Info,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        if auth_user.user_id != user_id and not auth_user.is_superuser:
            raise PermissionDenied("You can only unfollow on your own behalf")
        service = OrganizationService(session)
        return await service.remove_follower(organization_id, user_id)

    # ================================================================
    # Invitation mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def create_invitation(
        self,
        info: Info,
        organization_id: uuid.UUID,
        email: str,
        role: str = "member",
    ) -> InvitationType:
        session = get_session(info)
        auth_user = get_auth_user(info)

        org_service = OrganizationService(session)
        member = await org_service.get_member(organization_id, auth_user.user_id)
        if not member or member.role != "admin":
            raise PermissionDenied("Only org admins can create invitations")

        token = str(uuid.uuid4()) + "." + str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7)

        invitation = Invitation(
            organization_id=organization_id,
            email=email,
            role=role,
            token=token,
            invited_by=auth_user.user_id,
            expires_at=expires_at,
        )
        session.add(invitation)
        await session.flush()

        org = await org_service.get_by_id(organization_id)
        invite_url = f"{settings.frontend_url}/auth/accept-invitation?token={token}"
        await send_invitation_email(session, email, org.name if org else "Organization", invite_url)

        await session.commit()
        return InvitationType(**invitation_to_type(invitation))

    @strawberry.mutation
    @require_auth
    async def accept_invitation(
        self,
        info: Info,
        token: str,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)

        result = await session.exec(
            select(Invitation).where(Invitation.token == token, Invitation.status == "pending")
        )
        invitation = result.first()
        if not invitation:
            raise ValueError("Invalid or expired invitation")
        if invitation.expires_at < datetime.utcnow():
            invitation.status = "expired"
            await session.commit()
            raise ValueError("Invitation has expired")
        if invitation.email != auth_user.user.email:
            raise ValueError("This invitation is for a different email address")

        invitation.status = "accepted"
        invitation.accepted_by = auth_user.user_id
        invitation.accepted_at = datetime.utcnow()

        org_service = OrganizationService(session)
        await org_service.add_member(invitation.organization_id, auth_user.user_id, invitation.role)

        notif_service = NotificationService(session)
        await notif_service.create(
            user_id=invitation.invited_by,
            notification_type="invitation_accepted",
            title="Invitation Accepted",
            message=f"{auth_user.user.email} accepted your invitation",
        )

        await session.commit()
        return True

    # ================================================================
    # Event mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def create_event(
        self,
        info: Info,
        input: CreateEventInput,
    ) -> EventType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        event_service = EventService(session)

        if input.organization_id:
            org_service = OrganizationService(session)
            member = await org_service.get_member(input.organization_id, auth_user.user_id)
            if not member or member.role not in ("admin",):
                raise PermissionDenied("You must be an admin of the organization to create events under it")

        event = await event_service.create(
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
            created_by=auth_user.user_id,
        )
        await session.flush()

        await event_service.add_organizer(
            event_id=event.id,
            user_id=auth_user.user_id,
            assigned_by=auth_user.user_id,
            is_owner=True,
        )
        await session.commit()

        return EventType(**event_to_type(event))

    @strawberry.mutation
    @require_auth
    async def update_event(
        self,
        info: Info,
        id: uuid.UUID,
        input: UpdateEventInput,
    ) -> Optional[EventType]:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = EventService(session)

        event = await service.get_by_id(id)
        if not event:
            return None

        await service.ensure_organizer(id, auth_user.user_id)

        update_data = {k: v for k, v in input.__dict__.items() if v is not None}
        event = await service.update(event, **update_data)
        await session.commit()
        return EventType(**event_to_type(event))

    @strawberry.mutation
    @require_auth
    async def delete_event(
        self,
        info: Info,
        id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = EventService(session)

        event = await service.get_by_id(id)
        if not event:
            return False

        await service.ensure_organizer(id, auth_user.user_id)
        await service.delete(event)
        await session.commit()
        return True

    @strawberry.mutation
    @require_auth
    async def add_event_organizer(
        self,
        info: Info,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> EventStaffType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = EventService(session)

        await service.ensure_organizer(event_id, auth_user.user_id)

        staff = await service.add_organizer(
            event_id=event_id,
            user_id=user_id,
            assigned_by=auth_user.user_id,
            is_owner=False,
        )
        await session.commit()
        return EventStaffType(**event_staff_to_type(staff))

    @strawberry.mutation
    @require_auth
    async def remove_event_organizer(
        self,
        info: Info,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = EventService(session)

        await service.ensure_organizer(event_id, auth_user.user_id)

        result = await session.exec(
            select(EventStaff).where(
                EventStaff.event_id == event_id,
                EventStaff.user_id == user_id,
                EventStaff.is_active == True,
            )
        )
        staff = result.first()
        if not staff:
            return False
        if staff.is_owner and staff.user_id != auth_user.user_id:
            raise PermissionDenied("Only the owner can remove themselves as owner-organizer")
        staff.is_active = False
        await session.commit()
        return True

    @strawberry.mutation
    @require_auth
    async def transfer_event_ownership(
        self,
        info: Info,
        event_id: uuid.UUID,
        new_owner_id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = EventService(session)

        await service.ensure_organizer(event_id, auth_user.user_id)

        old_owner = await session.exec(
            select(EventStaff).where(
                EventStaff.event_id == event_id,
                EventStaff.user_id == auth_user.user_id,
                EventStaff.is_owner == True,
                EventStaff.is_active == True,
            )
        )

        new_owner_staff = await session.exec(
            select(EventStaff).where(
                EventStaff.event_id == event_id,
                EventStaff.user_id == new_owner_id,
                EventStaff.is_active == True,
            )
        )

        old = old_owner.first()
        new = new_owner_staff.first()

        if not old:
            raise PermissionDenied("Only the current owner can transfer ownership")

        if not new:
            new = await service.add_organizer(
                event_id=event_id,
                user_id=new_owner_id,
                assigned_by=auth_user.user_id,
                is_owner=False,
            )

        old.is_owner = False
        new.is_owner = True
        await session.commit()
        return True

    # ================================================================
    # Ticket mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def create_ticket(
        self,
        info: Info,
        input: CreateTicketInput,
    ) -> TicketType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(input.event_id, auth_user.user_id)

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
    @require_auth
    async def update_ticket(
        self,
        info: Info,
        id: uuid.UUID,
        input: UpdateTicketInput,
    ) -> Optional[TicketType]:
        session = get_session(info)
        service = TicketService(session)
        ticket = await service.get_by_id(id)
        if not ticket:
            return None

        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(ticket.event_id, auth_user.user_id)

        update_data = {k: v for k, v in input.__dict__.items() if v is not None}
        ticket = await service.update(ticket, **update_data)
        await session.commit()
        return TicketType(**ticket_to_type(ticket))

    @strawberry.mutation
    @require_auth
    async def delete_ticket(
        self,
        info: Info,
        id: uuid.UUID,
    ) -> bool:
        session = get_session(info)
        service = TicketService(session)
        ticket = await service.get_by_id(id)
        if not ticket:
            return False

        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(ticket.event_id, auth_user.user_id)

        await service.deactivate(ticket)
        await session.commit()
        return True

    # ================================================================
    # Order mutations
    # ================================================================

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
    @require_auth
    async def confirm_order(
        self,
        info: Info,
        id: uuid.UUID,
    ) -> Optional[OrderType]:
        session = get_session(info)
        event_service = EventService(session)
        service = OrderService(session)
        order = await service.get_by_id(id)
        if not order:
            return None

        auth_user = get_auth_user(info)
        await event_service.ensure_organizer(order.event_id, auth_user.user_id)

        order = await service.confirm_order(order)
        await session.commit()
        return OrderType(**order_to_type(order))

    @strawberry.mutation
    @require_auth
    async def cancel_order(
        self,
        info: Info,
        id: uuid.UUID,
        release_tickets: bool = True,
    ) -> Optional[OrderType]:
        session = get_session(info)
        service = OrderService(session)
        order = await service.get_by_id(id)
        if not order:
            return None

        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(order.event_id, auth_user.user_id)

        order = await service.cancel_order(order, release_tickets=release_tickets)
        await session.commit()
        return OrderType(**order_to_type(order))

    # ================================================================
    # Attendee mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def check_in_attendee(
        self,
        info: Info,
        attendee_id: uuid.UUID,
    ) -> Optional[AttendeeType]:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = AttendeeService(session)
        try:
            attendee = await service.check_in(attendee_id, auth_user.user_id)
            await session.commit()
            return AttendeeType(**attendee_to_type(attendee))
        except ValueError:
            await session.rollback()
            return None

    @strawberry.mutation
    @require_auth
    async def undo_attendee_check_in(
        self,
        info: Info,
        attendee_id: uuid.UUID,
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
    @require_auth
    async def update_attendee_notes(
        self,
        info: Info,
        attendee_id: uuid.UUID,
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

    # ================================================================
    # Payment mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def create_payment(
        self,
        info: Info,
        order_id: uuid.UUID,
        provider: str,
        provider_payment_id: str,
        amount: float,
        currency: str = "USD",
        payment_method: Optional[str] = None,
    ) -> Optional[PaymentType]:
        session = get_session(info)
        service = PaymentService(session)
        try:
            payment = await service.create_payment(
                order_id=order_id,
                provider=provider,
                provider_payment_id=provider_payment_id,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
            )
            await session.commit()
            return PaymentType(**payment_to_type(payment))
        except ValueError:
            await session.rollback()
            return None

    @strawberry.mutation
    @require_auth
    @require_role("admin")
    async def process_refund(
        self,
        info: Info,
        provider_payment_id: str,
        refund_amount: float,
        refund_reason: Optional[str] = None,
    ) -> Optional[PaymentType]:
        session = get_session(info)
        service = PaymentService(session)
        try:
            payment = await service.process_refund(
                provider_payment_id=provider_payment_id,
                refund_amount=refund_amount,
                refund_reason=refund_reason,
            )
            await session.commit()
            return PaymentType(**payment_to_type(payment)) if payment else None
        except ValueError:
            await session.rollback()
            return None

    # ================================================================
    # Payment provider mutations
    # ================================================================

    @strawberry.mutation
    async def create_payment_order(
        self,
        info: Info,
        order_id: uuid.UUID,
        provider: str = "razorpay",
    ) -> PaymentOrderPayload:
        session = get_session(info)
        service = OrderService(session)

        order = await service.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.payment_status != "unpaid":
            raise ValueError("Order already has a payment")

        payment_provider = get_provider(provider)
        amount_subunits = int(order.total_amount * 100)

        provider_order = await payment_provider.create_order(
            amount=amount_subunits,
            currency=order.currency,
            receipt=order.order_number,
            notes={"order_id": str(order.id), "order_number": order.order_number},
        )

        payment_service = PaymentService(session)
        await payment_service.create_payment(
            order_id=order.id,
            provider=provider,
            provider_payment_id=provider_order["id"],
            amount=float(order.total_amount),
            currency=order.currency,
        )
        await session.commit()

        return PaymentOrderPayload(
            provider_order_id=provider_order["id"],
            provider_key_id=payment_provider.public_key or "",
            order_id=order.id,
            order_number=order.order_number,
            amount=amount_subunits,
            currency=order.currency,
        )

    @strawberry.mutation
    async def verify_payment(
        self,
        info: Info,
        order_id: uuid.UUID,
        provider_payment_id: str,
        provider_order_id: str,
        signature: str,
        provider: str = "razorpay",
    ) -> PaymentVerificationResult:
        session = get_session(info)
        service = PaymentService(session)
        payment_provider = get_provider(provider)

        is_valid = payment_provider.verify_signature(
            provider_order_id=provider_order_id,
            payment_id=provider_payment_id,
            signature=signature,
        )

        if not is_valid:
            return PaymentVerificationResult(
                success=False,
                order_id=order_id,
                payment_status="unpaid",
                message="Invalid payment signature",
            )

        payment = await service.get_by_provider_payment_id(provider_order_id)
        if not payment:
            return PaymentVerificationResult(
                success=False,
                order_id=order_id,
                payment_status="unpaid",
                message="Payment record not found",
            )

        payment = await service.mark_payment_success(
            provider_payment_id=provider_order_id,
            extra_data={
                "provider_payment_id": provider_payment_id,
                "verified_via": "checkout_callback",
            },
        )
        await session.commit()

        return PaymentVerificationResult(
            success=True,
            order_id=order_id,
            payment_status=payment.status,
            message="Payment verified",
        )

    # ================================================================
    # Notification mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def mark_notification_read(
        self,
        info: Info,
        notification_id: uuid.UUID,
    ) -> Optional[NotificationType]:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = NotificationService(session)
        notif = await service.mark_read(notification_id)
        if not notif or notif.user_id != auth_user.user_id:
            return None
        await session.commit()
        return NotificationType(**notification_to_type(notif))

    @strawberry.mutation
    @require_auth
    async def mark_all_notifications_read(
        self,
        info: Info,
    ) -> int:
        session = get_session(info)
        auth_user = get_auth_user(info)
        service = NotificationService(session)
        count = await service.mark_all_read(auth_user.user_id)
        return count

    # ================================================================
    # Event Page Builder mutations
    # ================================================================

    @strawberry.mutation
    @require_auth
    async def save_event_page(
        self,
        info: Info,
        event_id: uuid.UUID,
        input: UpdateEventPageInput,
    ) -> EventPageType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(event_id, auth_user.user_id)

        page_service = EventPageService(session)

        blocks = []
        for b in input.blocks:
            block_data = {
                "id": b.id,
                "type": b.type,
                "visible": b.visible,
            }
            if b.props is not None:
                block_data["props"] = b.props
            else:
                block_data["props"] = {}
            blocks.append(block_data)

        page = await page_service.update_blocks(event_id, blocks)
        if input.is_published:
            page = await page_service.publish(event_id)

        await session.commit()
        return EventPageType(**event_page_to_type(page))

    @strawberry.mutation
    @require_auth
    async def publish_event_page(
        self,
        info: Info,
        event_id: uuid.UUID,
    ) -> EventPageType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(event_id, auth_user.user_id)

        page_service = EventPageService(session)
        page = await page_service.publish(event_id)
        await session.commit()
        return EventPageType(**event_page_to_type(page))

    @strawberry.mutation
    @require_auth
    async def unpublish_event_page(
        self,
        info: Info,
        event_id: uuid.UUID,
    ) -> EventPageType:
        session = get_session(info)
        auth_user = get_auth_user(info)
        event_service = EventService(session)
        await event_service.ensure_organizer(event_id, auth_user.user_id)

        page_service = EventPageService(session)
        page = await page_service.unpublish(event_id)
        await session.commit()
        return EventPageType(**event_page_to_type(page))
