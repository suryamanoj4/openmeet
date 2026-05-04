"""Tests for domain services using SQLite."""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlmodel import select

from auth import hash_password
from gql_schema.services import (
    AttendeeService,
    EventService,
    OrderService,
    OrganizationService,
    PaymentService,
    TicketService,
    UserService,
)
from models import (
    Attendee,
    Event,
    Follower,
    Member,
    Order,
    OrderItem,
    Organization,
    Payment,
    Ticket,
    User,
)

_counter = 0
def _next_email() -> str:
    global _counter
    _counter += 1
    return f"ts{_counter}@example.com"


class TestUserService:
    async def test_create_user(self, db_session):
        svc = UserService(db_session)
        user = await svc.create(
            User,
            email="new@test.com",
            password_hash="hashed_pw",
            first_name="New",
            last_name="User",
        )
        await db_session.commit()
        assert user.id is not None
        assert user.email == "new@test.com"

    async def test_get_by_email(self, db_session, seeded_user):
        svc = UserService(db_session)
        found = await svc.get_by_email(seeded_user.email)
        assert found is not None
        assert found.id == seeded_user.id

    async def test_get_by_email_not_found(self, db_session):
        svc = UserService(db_session)
        assert await svc.get_by_email("nonexistent@test.com") is None

    async def test_get_by_id(self, db_session, seeded_user):
        svc = UserService(db_session)
        found = await svc.get_by_id(seeded_user.id)
        assert found is not None
        assert found.email == seeded_user.email

    async def test_get_all(self, db_session, seeded_user):
        svc = UserService(db_session)
        await svc.create(User, email="user2@test.com", password_hash="pw", first_name="U2", last_name="User")
        await db_session.commit()
        users = await svc.get_all()
        assert len(users) >= 2

    async def test_update_user(self, db_session, seeded_user):
        svc = UserService(db_session)
        updated = await svc.update(seeded_user, first_name="Updated")
        await db_session.commit()
        assert updated.first_name == "Updated"

    async def test_delete_user(self, db_session, seeded_user):
        svc = UserService(db_session)
        await svc.delete(seeded_user)
        await db_session.commit()
        assert await svc.get_by_id(seeded_user.id) is None


class TestOrganizationService:
    async def test_create_organization(self, db_session, seeded_user):
        svc = OrganizationService(db_session)
        org = await svc.create(Organization, name="New Org", slug="new-org")
        await db_session.commit()
        assert org.id is not None

    async def test_add_member(self, db_session, seeded_org, seeded_user):
        svc = OrganizationService(db_session)
        new_member = User(
            email=_next_email(),
            password_hash=hash_password("pw"),
            first_name="New",
            last_name="Member",
        )
        db_session.add(new_member)
        await db_session.flush()
        member = await svc.add_member(seeded_org.id, new_member.id, "member")
        await db_session.commit()
        assert member is not None
        assert member.user_id == new_member.id
        members = await svc.get_members(seeded_org.id)
        assert len(members) >= 1

    async def test_add_follower(self, db_session, seeded_org, seeded_user):
        svc = OrganizationService(db_session)
        await svc.add_follower(seeded_org.id, seeded_user.id)
        await db_session.commit()
        followers = await svc.get_followers(seeded_org.id)
        assert any(f.user_id == seeded_user.id for f in followers)

    async def test_remove_follower(self, db_session, seeded_org, seeded_user):
        svc = OrganizationService(db_session)
        await svc.add_follower(seeded_org.id, seeded_user.id)
        await db_session.commit()
        removed = await svc.remove_follower(seeded_org.id, seeded_user.id)
        await db_session.commit()
        assert removed is True
        followers = await svc.get_followers(seeded_org.id)
        assert all(not f.is_active for f in followers if f.user_id == seeded_user.id)


class TestEventService:
    async def test_create_event(self, db_session, seeded_org):
        svc = EventService(db_session)
        event = await svc.create(
            Event,
            organization_id=seeded_org.id,
            name="My Event",
            slug="my-event",
            event_type="workshop",
            status="draft",
            visibility="public",
            start_date=datetime.utcnow() + timedelta(days=10),
            end_date=datetime.utcnow() + timedelta(days=11),
        )
        await db_session.commit()
        assert event.id is not None

    async def test_get_tickets(self, db_session, seeded_event, seeded_ticket):
        svc = EventService(db_session)
        tickets = await svc.get_tickets(seeded_event.id)
        assert len(tickets) == 1
        assert tickets[0].id == seeded_ticket.id

    async def test_get_orders(self, db_session, seeded_event):
        svc = EventService(db_session)
        orders = await svc.get_orders(seeded_event.id)
        assert orders == []


class TestTicketService:
    async def test_create_and_get_ticket(self, db_session, seeded_event):
        svc = TicketService(db_session)
        ticket = await svc.create(
            Ticket,
            event_id=seeded_event.id,
            name="VIP",
            price=5000.0,
            currency="USD",
            quantity=50,
            sort_order=1,
        )
        await db_session.commit()
        assert ticket.id is not None

        fetched = await svc.get_by_id(ticket.id)
        assert fetched.name == "VIP"

    async def test_available_tickets(self, db_session, seeded_event, seeded_ticket):
        svc = TicketService(db_session)
        available = await svc.get_available_tickets(seeded_event.id)
        assert all(
            t.is_active and t.sold_quantity < t.quantity for t in available
        )

    async def test_reserve_and_release(self, db_session, seeded_ticket):
        svc = TicketService(db_session)
        result = await svc.check_availability(seeded_ticket.id, 5)
        assert result is True

        await svc.reserve_tickets(seeded_ticket.id, 5)
        await db_session.commit()
        ticket = await svc.get_by_id(seeded_ticket.id)
        assert ticket.sold_quantity == 5

        await svc.release_tickets(seeded_ticket.id, 3)
        await db_session.commit()
        ticket = await svc.get_by_id(seeded_ticket.id)
        assert ticket.sold_quantity == 2

    async def test_check_availability_insufficient(self, db_session, seeded_ticket):
        svc = TicketService(db_session)
        result = await svc.check_availability(seeded_ticket.id, 999)
        assert result is False


class TestOrderService:
    async def test_create_order(self, db_session, seeded_event, seeded_ticket):
        svc = OrderService(db_session)
        order = await svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John Buyer",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 2}],
        )
        await db_session.commit()
        assert order.order_number.startswith("OM-")
        assert order.status == "pending"
        assert order.total_amount == 2000.0
        assert seeded_ticket.sold_quantity == 2

    async def test_create_order_event_not_found(self, db_session):
        svc = OrderService(db_session)
        with pytest.raises(ValueError, match="Event not found"):
            await svc.create_order(
                event_id=uuid.uuid4(),
                customer_email="buyer@test.com",
                customer_name="John",
                customer_phone=None,
                items=[],
            )

    async def test_confirm_order(self, db_session, seeded_event, seeded_ticket):
        svc = OrderService(db_session)
        order = await svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )

        confirmed = await svc.confirm_order(order)
        await db_session.commit()
        assert confirmed.status == "confirmed"
        assert confirmed.payment_status == "paid"
        assert confirmed.confirmed_at is not None

    async def test_cancel_order_releases_tickets(
        self, db_session, seeded_event, seeded_ticket
    ):
        svc = OrderService(db_session)
        order = await svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 3}],
        )
        await db_session.refresh(order, ["items"])
        initial_sold = seeded_ticket.sold_quantity

        cancelled = await svc.cancel_order(order, release_tickets=True)
        await db_session.commit()
        assert cancelled.status == "cancelled"
        assert seeded_ticket.sold_quantity == initial_sold - 3

    async def test_generate_order_number(self, db_session):
        svc = OrderService(db_session)
        num = svc.generate_order_number()
        assert num.startswith("OM-")
        assert len(num) == 18  # OM-YYYYMMDD-XXXXXX

    async def test_get_by_order_number(self, db_session, seeded_event, seeded_ticket):
        svc = OrderService(db_session)
        order = await svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()
        found = await svc.get_by_order_number(order.order_number)
        assert found is not None
        assert found.id == order.id


class TestAttendeeService:
    async def test_create_attendee(self, db_session, seeded_event, seeded_ticket):
        order_svc = OrderService(db_session)
        attendee_svc = AttendeeService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()
        await db_session.refresh(order, ["items"])
        item = order.items[0]

        attendee = await attendee_svc.create(
            Attendee,
            order_item_id=item.id,
            ticket_id=seeded_ticket.id,
            first_name="Jane",
            last_name="Doe",
            email="jane@test.com",
        )
        await db_session.commit()
        assert attendee.id is not None

    async def test_check_in(self, db_session, seeded_user, seeded_event, seeded_ticket):
        order_svc = OrderService(db_session)
        attendee_svc = AttendeeService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()
        await db_session.refresh(order, ["items"])
        item = order.items[0]

        attendee = await attendee_svc.create(
            Attendee,
            order_item_id=item.id,
            ticket_id=seeded_ticket.id,
            first_name="Jane",
            last_name="Doe",
            email="jane@test.com",
        )
        await db_session.commit()

        checked_in = await attendee_svc.check_in(attendee.id, seeded_user.id)
        await db_session.commit()
        assert checked_in.check_in_status is True

        undone = await attendee_svc.undo_check_in(attendee.id)
        await db_session.commit()
        assert undone.check_in_status is False


class TestPaymentService:
    async def test_create_payment(self, db_session, seeded_event, seeded_ticket):
        order_svc = OrderService(db_session)
        payment_svc = PaymentService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()

        payment = await payment_svc.create_payment(
            order_id=order.id,
            provider="razorpay",
            provider_payment_id="order_test_123",
            amount=1000.0,
            currency="INR",
        )
        await db_session.commit()
        assert payment.id is not None
        assert payment.status == "pending"

    async def test_mark_payment_success_and_order_confirmed(
        self, db_session, seeded_event, seeded_ticket
    ):
        order_svc = OrderService(db_session)
        payment_svc = PaymentService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()

        await payment_svc.create_payment(
            order_id=order.id,
            provider="razorpay",
            provider_payment_id="order_test_456",
            amount=1000.0,
            currency="INR",
        )
        await db_session.commit()

        success = await payment_svc.mark_payment_success("order_test_456")
        await db_session.commit()
        assert success is not None
        assert success.status == "completed"

        await db_session.refresh(order)
        assert order.status == "confirmed"
        assert order.payment_status == "paid"

    async def test_mark_payment_failed(self, db_session, seeded_event, seeded_ticket):
        order_svc = OrderService(db_session)
        payment_svc = PaymentService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()

        await payment_svc.create_payment(
            order_id=order.id,
            provider="razorpay",
            provider_payment_id="order_test_789",
            amount=1000.0,
            currency="INR",
        )
        await db_session.commit()

        failed = await payment_svc.mark_payment_failed(
            "order_test_789", failure_reason="Insufficient funds"
        )
        await db_session.commit()
        assert failed.status == "failed"
        assert failed.failure_reason == "Insufficient funds"

    async def test_process_refund(self, db_session, seeded_event, seeded_ticket):
        order_svc = OrderService(db_session)
        payment_svc = PaymentService(db_session)

        order = await order_svc.create_order(
            event_id=seeded_event.id,
            customer_email="buyer@test.com",
            customer_name="John",
            customer_phone=None,
            items=[{"ticket_id": seeded_ticket.id, "quantity": 1}],
        )
        await db_session.commit()

        await payment_svc.create_payment(
            order_id=order.id,
            provider="razorpay",
            provider_payment_id="order_test_refund",
            amount=1000.0,
            currency="INR",
        )
        await db_session.commit()
        await payment_svc.mark_payment_success("order_test_refund")
        await db_session.commit()

        refunded = await payment_svc.process_refund(
            "order_test_refund", refund_amount=500.0, refund_reason="Partial refund"
        )
        await db_session.commit()
        assert refunded.status == "refunded"
        assert refunded.refunded_amount == 500.0
