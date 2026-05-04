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
        "member_id": staff.member_id,
        "role": staff.role,
        "assigned_at": staff.assigned_at,
        "is_active": staff.is_active,
        "created_at": staff.created_at,
        "updated_at": staff.updated_at,
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