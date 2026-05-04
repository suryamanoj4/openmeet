"""Database seeder — populates the DB with realistic fake data for development."""

import asyncio
import random
import string
from datetime import datetime, timedelta

from faker import Faker

from auth import hash_password
from database import async_engine, AsyncSessionLocal
from models import (
    User,
    Organization,
    Member,
    Follower,
    Event,
    Ticket,
    Order,
    OrderItem,
    Attendee,
    Payment,
)

fake = Faker()
_event_types = ["conference", "workshop", "meetup", "webinar", "hackathon"]
_venues = [
    "Grand Convention Center",
    "TechHub Auditorium",
    "Innovation Lab",
    "Downtown Conference Hall",
    "Skyline Event Space",
    None,
]
_cities = ["San Francisco", "New York", "London", "Berlin", "Bangalore", "Singapore"]


def _order_number() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d")
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"OM-{ts}-{rand}"


def _slug(text: str) -> str:
    return text.lower().replace(" ", "-").replace(".", "")[:50]


async def seed():
    async with AsyncSessionLocal() as session:
        # ---------- Users ----------
        admin = User(
            email="admin@openmeet.local",
            password_hash=hash_password("password123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role="admin",
            is_superuser=True,
            is_email_verified=True,
        )
        org1_owner = User(
            email="organizer1@openmeet.local",
            password_hash=hash_password("password123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role="organizer",
            is_email_verified=True,
        )
        org2_owner = User(
            email="organizer2@openmeet.local",
            password_hash=hash_password("password123"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role="organizer",
            is_email_verified=True,
        )

        regular_users = []
        for i in range(8):
            regular_users.append(
                User(
                    email=f"user{i+1}@openmeet.local",
                    password_hash=hash_password("password123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role="user",
                    is_email_verified=True,
                )
            )

        session.add_all([admin, org1_owner, org2_owner] + regular_users)
        await session.flush()

        # -------- Organizations ----------
        orgs = []
        org_data = [
            {"name": "TechConf Global", "slug": "techconf-global", "owner": org1_owner, "desc": "The premier technology conference bringing together developers, designers, and innovators from around the world."},
            {"name": "Design Masters", "slug": "design-masters", "owner": org2_owner, "desc": "A community of design professionals hosting workshops, meetups, and conferences on UX, UI, and product design."},
            {"name": "Data Science Hub", "slug": "data-science-hub", "owner": org1_owner, "desc": "Connecting data scientists, ML engineers, and analytics professionals through regular events and hackathons."},
            {"name": "Startup Founders Club", "slug": "startup-founders-club", "owner": org2_owner, "desc": "Monthly meetups and annual conference for startup founders to network, share knowledge, and find co-founders."},
        ]

        for d in org_data:
            org = Organization(
                name=d["name"],
                slug=d["slug"],
                description=d["desc"],
                website_url=f"https://{d['slug']}.com",
                social_links={"twitter": f"@{d['slug']}", "linkedin": f"/company/{d['slug']}"},
                settings={"theme_color": "#4F46E5", "enable_waitlist": True},
            )
            session.add(org)
            await session.flush()
            orgs.append(org)

            # Owner as admin member
            session.add(Member(user_id=d["owner"].id, organization_id=org.id, role="admin"))
            await session.flush()

            # Add 3-5 random members to each org
            member_count = random.randint(3, 5)
            for user in random.sample(regular_users, member_count):
                session.add(Member(user_id=user.id, organization_id=org.id, role=random.choice(["member", "organizer"])))

            # Add 4-8 random followers to each org
            follower_pool = [admin, org1_owner, org2_owner] + regular_users
            follower_count = random.randint(4, 8)
            for user in random.sample(follower_pool, min(follower_count, len(follower_pool))):
                if user.id != d["owner"].id:
                    session.add(Follower(user_id=user.id, organization_id=org.id))

        await session.flush()

        # -------- Events ----------
        all_events = []
        for org in orgs:
            for i in range(random.randint(3, 5)):
                start_date = fake.date_time_between(start_date="+30d", end_date="+180d")
                status = random.choice(["draft", "published", "published", "published"])  # mostly published
                venue = random.choice(_venues)

                event = Event(
                    organization_id=org.id,
                    name=fake.catch_phrase(),
                    slug=_slug(fake.catch_phrase()) + f"-{i}",
                    description="\n".join(fake.paragraphs(nb=2)),
                    event_type=random.choice(_event_types),
                    status=status,
                    visibility=random.choice(["public", "public", "private"]),
                    start_date=start_date,
                    end_date=start_date + timedelta(hours=random.choice([3, 6, 8, 24, 48])),
                    timezone=random.choice(["America/New_York", "Europe/London", "Asia/Kolkata", "UTC"]),
                    venue_name=venue,
                    venue_address={"line1": fake.street_address(), "city": random.choice(_cities), "country": fake.country()} if venue else None,
                    venue_city=random.choice(_cities) if venue else None,
                    venue_country=fake.country() if venue else None,
                    is_online=venue is None,
                    online_url=f"https://meet.{org.slug}.com/{_slug(fake.word())}" if venue is None else None,
                    max_attendees=random.choice([50, 100, 200, 500, 1000, None]),
                    cover_image_url=f"https://picsum.photos/seed/{random.randint(1,1000)}/800/400",
                    settings={"enable_networking": True, "enable_qna": True},
                )
                session.add(event)
                await session.flush()
                all_events.append(event)

                # -------- Tickets ----------
                ticket_configs = [
                    {"name": "Early Bird", "price": random.randint(500, 2000), "quantity": random.randint(10, 50)},
                    {"name": "Regular", "price": random.randint(2000, 5000), "quantity": random.randint(50, 200)},
                    {"name": "VIP", "price": random.randint(5000, 15000), "quantity": random.randint(5, 30)},
                ]
                for j, tc in enumerate(ticket_configs[: random.randint(2, 3)]):
                    ticket = Ticket(
                        event_id=event.id,
                        name=tc["name"],
                        description=f"{tc['name']} access to {event.name}",
                        price=float(tc["price"]),
                        currency=random.choice(["USD", "INR"]),
                        quantity=tc["quantity"],
                        sort_order=j,
                    )
                    session.add(ticket)
                    await session.flush()

                    # If event is published, create some orders
                    if status == "published":
                        for _ in range(random.randint(3, 8)):
                            max_qty = min(3, ticket.quantity - ticket.sold_quantity)
                            if max_qty <= 0:
                                break
                            order_qty = random.randint(1, max_qty)
                            customer_name = fake.name()
                            customer_email = fake.email()
                            unit_price = float(tc["price"])
                            total = unit_price * order_qty

                            order = Order(
                                event_id=event.id,
                                order_number=_order_number(),
                                status=random.choices(["confirmed", "confirmed", "pending"], weights=[7, 7, 3])[0],
                                customer_email=customer_email,
                                customer_name=customer_name,
                                customer_phone=fake.phone_number()[:20],
                                subtotal=total,
                                total_amount=total,
                                currency=ticket.currency,
                                payment_status=random.choices(["paid", "paid", "unpaid"], weights=[7, 7, 2])[0],
                                confirmed_at=datetime.utcnow() if random.random() > 0.2 else None,
                            )
                            session.add(order)
                            await session.flush()

                            order_item = OrderItem(
                                order_id=order.id,
                                ticket_id=ticket.id,
                                quantity=order_qty,
                                unit_price=unit_price,
                                total_price=total,
                            )
                            session.add(order_item)
                            await session.flush()

                            ticket.sold_quantity += order_qty

                            # -------- Attendees ----------
                            for _ in range(order_qty):
                                attendee = Attendee(
                                    order_item_id=order_item.id,
                                    ticket_id=ticket.id,
                                    first_name=fake.first_name(),
                                    last_name=fake.last_name(),
                                    email=fake.email(),
                                    phone=fake.phone_number()[:20],
                                    company=fake.company(),
                                    job_title=fake.job(),
                                    check_in_status=random.random() > 0.6,
                                    check_in_at=datetime.utcnow() if random.random() > 0.7 else None,
                                )
                                session.add(attendee)
                                await session.flush()

                            # -------- Payments ----------
                            if order.payment_status == "paid":
                                payment = Payment(
                                    order_id=order.id,
                                    provider="razorpay",
                                    provider_payment_id=f"pay_{fake.uuid4()}",
                                    amount=total,
                                    currency=ticket.currency,
                                    status="completed",
                                    payment_method=random.choice(["upi", "card", "netbanking", "wallet"]),
                                    extra_data={
                                        "razorpay_order_id": f"order_{fake.uuid4()}",
                                        "razorpay_payment_id": f"pay_{fake.uuid4()}",
                                    },
                                )
                                session.add(payment)
                                await session.flush()

        await session.commit()

        # Summary
        org_count = len(orgs)
        event_count = len(all_events)
        ticket_count = await session.connection()
        print(f"Seeded: 11 users | {org_count} orgs | {event_count} events | with tickets, orders, attendees, payments")


if __name__ == "__main__":
    asyncio.run(seed())
