"""Type mapping utilities for GraphQL."""

from typing import Type, Any, Dict, Callable
from uuid import UUID


class TypeMapper:
    """Maps SQLAlchemy models to Strawberry GraphQL types."""

    def __init__(self):
        self._mappings: Dict[Type, Callable] = {}

    def register(self, model_class: Type, mapper_fn: Callable):
        self._mappings[model_class] = mapper_fn

    def map(self, instance, gql_type_class: Type) -> Any:
        """Map model instance to GraphQL type."""
        if mapper := self._mappings.get(type(instance)):
            return mapper(instance)
        raise ValueError(f"No mapper registered for {type(instance)}")


type_mapper = TypeMapper()


def user_to_type(user) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_email_verified": user.is_email_verified,
        "role": user.role,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def organization_to_type(org) -> dict:
    return {
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "description": org.description,
        "logo_url": org.logo_url,
        "website_url": org.website_url,
        "social_links": org.social_links,
        "settings": org.settings,
        "is_verified": org.is_verified,
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }


def event_to_type(event) -> dict:
    return {
        "id": event.id,
        "organization_id": event.organization_id,
        "name": event.name,
        "slug": event.slug,
        "description": event.description,
        "event_type": event.event_type,
        "status": event.status,
        "visibility": event.visibility,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "timezone": event.timezone,
        "venue_name": event.venue_name,
        "venue_address": event.venue_address,
        "venue_city": event.venue_city,
        "venue_country": event.venue_country,
        "is_online": event.is_online,
        "online_url": event.online_url,
        "max_attendees": event.max_attendees,
        "min_tickets_per_order": event.min_tickets_per_order,
        "max_tickets_per_order": event.max_tickets_per_order,
        "registration_start": event.registration_start,
        "registration_end": event.registration_end,
        "cover_image_url": event.cover_image_url,
        "banner_image_url": event.banner_image_url,
        "settings": event.settings,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }


def ticket_to_type(ticket) -> dict:
    return {
        "id": ticket.id,
        "event_id": ticket.event_id,
        "name": ticket.name,
        "description": ticket.description,
        "price": ticket.price,
        "currency": ticket.currency,
        "quantity": ticket.quantity,
        "sold_quantity": ticket.sold_quantity,
        "min_per_order": ticket.min_per_order,
        "max_per_order": ticket.max_per_order,
        "sale_start": ticket.sale_start,
        "sale_end": ticket.sale_end,
        "sort_order": ticket.sort_order,
        "is_active": ticket.is_active,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
    }


def order_to_type(order) -> dict:
    return {
        "id": order.id,
        "event_id": order.event_id,
        "order_number": order.order_number,
        "status": order.status,
        "customer_email": order.customer_email,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "subtotal": order.subtotal,
        "tax_amount": order.tax_amount,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "payment_status": order.payment_status,
        "notes": order.notes,
        "extra_data": order.extra_data,
        "expires_at": order.expires_at,
        "confirmed_at": order.confirmed_at,
        "cancelled_at": order.cancelled_at,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def order_item_to_type(item) -> dict:
    return {
        "id": item.id,
        "order_id": item.order_id,
        "ticket_id": item.ticket_id,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "total_price": item.total_price,
        "created_at": item.created_at,
    }


def attendee_to_type(attendee) -> dict:
    return {
        "id": attendee.id,
        "order_item_id": attendee.order_item_id,
        "ticket_id": attendee.ticket_id,
        "first_name": attendee.first_name,
        "last_name": attendee.last_name,
        "email": attendee.email,
        "phone": attendee.phone,
        "company": attendee.company,
        "job_title": attendee.job_title,
        "custom_data": attendee.custom_data,
        "check_in_status": attendee.check_in_status,
        "check_in_at": attendee.check_in_at,
        "notes": attendee.notes,
        "created_at": attendee.created_at,
        "updated_at": attendee.updated_at,
    }


def payment_to_type(payment) -> dict:
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "provider": payment.provider,
        "provider_payment_id": payment.provider_payment_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "extra_data": payment.extra_data,
        "failure_reason": payment.failure_reason,
        "refunded_amount": payment.refunded_amount,
        "refund_reason": payment.refund_reason,
        "refunded_at": payment.refunded_at,
        "created_at": payment.created_at,
    }


def member_to_type(member) -> dict:
    return {
        "id": member.id,
        "user_id": member.user_id,
        "organization_id": member.organization_id,
        "role": member.role,
        "joined_at": member.joined_at,
        "is_active": member.is_active,
        "created_at": member.created_at,
        "updated_at": member.updated_at,
    }


def follower_to_type(follower) -> dict:
    return {
        "id": follower.id,
        "user_id": follower.user_id,
        "organization_id": follower.organization_id,
        "created_at": follower.created_at,
        "is_active": follower.is_active,
    }


def event_staff_to_type(staff) -> dict:
    return {
        "id": staff.id,
        "event_id": staff.event_id,
        "user_id": staff.user_id,
        "role": staff.role,
        "is_owner": staff.is_owner,
        "assigned_at": staff.assigned_at,
        "assigned_by": staff.assigned_by,
        "is_active": staff.is_active,
        "created_at": staff.created_at,
        "updated_at": staff.updated_at,
    }


def audit_log_to_type(log) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "organization_id": log.organization_id,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "changes": log.changes,
        "created_at": log.created_at,
    }


def email_log_to_type(log) -> dict:
    return {
        "id": log.id,
        "recipient_email": log.recipient_email,
        "template_name": log.template_name,
        "status": log.status,
        "error_message": log.error_message,
        "extra_data": log.extra_data,
        "created_at": log.created_at,
    }


def invitation_to_type(inv) -> dict:
    return {
        "id": inv.id,
        "organization_id": inv.organization_id,
        "email": inv.email,
        "role": inv.role,
        "status": inv.status,
        "token": inv.token,
        "invited_by": inv.invited_by,
        "accepted_by": inv.accepted_by,
        "expires_at": inv.expires_at,
        "accepted_at": inv.accepted_at,
        "created_at": inv.created_at,
        "updated_at": inv.updated_at,
    }


def notification_to_type(notif) -> dict:
    return {
        "id": notif.id,
        "user_id": notif.user_id,
        "notification_type": notif.notification_type,
        "title": notif.title,
        "message": notif.message,
        "data": notif.data,
        "is_read": notif.is_read,
        "read_at": notif.read_at,
        "created_at": notif.created_at,
    }


def event_page_to_type(page) -> dict:
    return {
        "id": page.id,
        "event_id": page.event_id,
        "blocks": page.blocks,
        "is_published": page.is_published,
        "published_at": page.published_at,
        "created_at": page.created_at,
        "updated_at": page.updated_at,
    }


def register_mappers():
    from models import (
        User,
        Organization,
        Event,
        Ticket,
        Order,
        OrderItem,
        Attendee,
        Payment,
        Member,
        Follower,
        EventStaff,
        AuditLog,
        EmailLog,
        Invitation,
        Notification,
        EventPage,
    )

    type_mapper.register(User, user_to_type)
    type_mapper.register(Organization, organization_to_type)
    type_mapper.register(Event, event_to_type)
    type_mapper.register(Ticket, ticket_to_type)
    type_mapper.register(Order, order_to_type)
    type_mapper.register(OrderItem, order_item_to_type)
    type_mapper.register(Attendee, attendee_to_type)
    type_mapper.register(Payment, payment_to_type)
    type_mapper.register(Member, member_to_type)
    type_mapper.register(Follower, follower_to_type)
    type_mapper.register(EventStaff, event_staff_to_type)
    type_mapper.register(AuditLog, audit_log_to_type)
    type_mapper.register(EmailLog, email_log_to_type)
    type_mapper.register(Invitation, invitation_to_type)
    type_mapper.register(Notification, notification_to_type)
    type_mapper.register(EventPage, event_page_to_type)