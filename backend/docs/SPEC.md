# OpenMeets Backend - Technical Specification

**Purpose:** Explain backend architecture AND guide backend developers

---

## What the Backend Does

The backend handles:
- User authentication and authorization
- Data storage and retrieval (PostgreSQL)
- Business logic (organizations, events, tickets, orders)
- Payment processing (Stripe, Razorpay)
- Background tasks (email, PDFs, reports)
- API delivery via GraphQL

---

## Architecture

### Structure

```
backend/
├── models/           # SQLAlchemy ORM models
├── gql_schema/       # GraphQL types, queries, mutations
│   ├── types/       # Strawberry type definitions
│   ├── inputs/      # Input types
│   ├── queries/    # Query definitions
│   ├── mutations/  # Mutation definitions
│   └── services/   # Business logic
├── alembic/         # Database migrations
└── main.py          # FastAPI entry point
```

### Technology

- FastAPI (0.115+) - Web framework
- Strawberry (0.200+) - GraphQL
- SQLAlchemy 2.0 (Async) - ORM
- PostgreSQL 15+ - Database
- Celery - Background tasks
- Redis - Cache + Celery broker

---

## GraphQL API

### Endpoints

- **Query:** All read operations
- **Mutation:** All write operations
- **Subscription:** (Future) Real-time updates

### Example Queries

```graphql
# Get event with tickets
query GetEvent($id: UUID!) {
  event(id: $id) {
    id
    name
    startDate
    tickets {
      id
      name
      price
      available: soldQuantity
    }
  }
}

# Create order
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    id
    orderNumber
    totalAmount
  }
}

# Check in attendee
mutation CheckInAttendee($id: UUID!) {
  checkInAttendee(id: $id) {
    checkInStatus
    checkInAt
  }
}
```

---

## Database

### Tables

All tables use UUID primary keys with soft delete (`is_active`).

| Table | Purpose |
|-------|---------|
| users | User accounts |
| organizations | Event hosts |
| members | User-org relationships |
| followers | User-org follows |
| events | Event records |
| tickets | Ticket types |
| orders | Purchases |
| order_items | Tickets in orders |
| attendees | Ticket holders |
| payments | Transactions |
| audit_logs | Action history |

---

## Services

### Service Pattern

Each service handles CRUD + business logic:

```python
class EventService(BaseService):
    model = Event
    
    async def create(self, ModelClass, **kwargs):
        # Business logic here
        return await super().create(...)
    
    async def publish(self, event_id):
        # Publish logic
        event = await self.get_by_id(event_id)
        event.status = "published"
        await self.db.commit()
        return event
```

### Required Services

| Service | Responsibility |
|---------|----------------|
| UserService | Auth, profile |
| OrganizationService | CRUD + members |
| EventService | CRUD + publishing |
| TicketService | CRUD + inventory |
| OrderService | CRUD + expiry |
| PaymentService | Provider integration |
| AttendeeService | CRUD + check-in |
| EmailService | Send emails |
| NotificationService | In-app notifications |

---

## Background Tasks (Celery)

### Tasks to Implement

| Task | Trigger | Priority |
|------|---------|----------|
| release_expired_orders | Cron (1 min) | High |
| process_payment_webhook | Webhook | High |
| send_email | API call | High |
| generate_ticket_pdf | Payment confirmed | High |
| send_event_reminders | Cron (daily) | Medium |
| export_attendees | User request | Low |

### Celery Setup

```python
# tasks.py
@celery.task
def release_expired_orders():
    """Release tickets for expired orders"""
    # Find expired orders
    # Release ticket quantities
    # Update order status
```

---

## Authentication

### JWT Flow

1. User logs in → Receive access (15 min) + refresh (7 days) tokens
2. Access token in Authorization header
3. Refresh when access expires

### Token Payload

```python
{
    "sub": "user-uuid",
    "type": "access",
    "exp": 1234567890
}
```

---

## Payment Integration

### Stripe

```python
# Create payment intent
stripe_intent = stripe.PaymentIntent.create(
    amount=int(total * 100),  # cents
    currency=currency.lower(),
    customer_email=email,
)
```

### Webhook Handling

```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key
    )
    
    if event.type == "payment_intent.succeeded":
        await confirm_order(event.data.object.metadata.order_id)
```

---

---

## Role & Permission System

Two separate domains:

### Platform-Level Roles (on `User`)

| Role | Level | Description |
|------|-------|-------------|
| `user` | 0 | Default. Browse events, register/buy tickets, create personal events, manage own profile |
| `admin` | 1 | Everything a user can, plus delete users, manage any event, platform admin |

- `is_superuser: true` bypasses all permission checks
- Role hierarchy enforced by `require_role("admin")` decorator in `auth.py`

### Event-Level Roles (on `EventStaff`)

The `EventStaff` model links users directly to events:

```
EventStaff
├── user_id      FK → users.id
├── event_id     FK → events.id
├── role         "organizer" (string, extensible for future roles)
├── is_owner     boolean — only the creator/owner can transfer ownership
├── assigned_by  FK → users.id
└── assigned_at  datetime
```

Rules:
- Every event has at least one `EventStaff` record with `role="organizer"`
- The creator gets `is_owner=true` — only they can transfer ownership
- Additional co-organizers can be added with `role="organizer"`, `is_owner=false`
- All organizers have equal editing power (except ownership transfer)
- Event role checked via `require_event_role(event_id, "organizer")` in `auth.py`

### Organization Membership (on `Member`)

- `Member.role`: `"admin"` or `"member"` (per-organization)
- Used for organization-level features (grouping events, team management)
- Event creation: user must be org admin to associate event with an org
- Personal events can be created without any org

### Participants vs Organizers

- **Participants** = users who registered/bought tickets → tracked via `Order` / `Attendee`
- **Organizers** = users who manage the event → tracked via `EventStaff`
- These are completely separate — a user can be both an organizer and a participant

---

## Implementation Order

### Step 1: Foundation
1. Set up FastAPI + Strawberry
2. Configure SQLAlchemy
3. Create base models (User, Organization, Event)

### Step 2: Auth
4. Implement registration/login
5. Set up JWT tokens
6. Add password reset

### Step 3: Core CRUD
7. Complete OrganizationService
8. Complete EventService
9. Complete TicketService

### Step 4: Orders & Payments
10. Implement OrderService
11. Add Stripe/Razorpay
12. Create webhook endpoints

### Step 5: Attendees
13. Implement AttendeeService
14. Add check-in functionality

### Step 6: Background Tasks
15. Configure Celery
16. Implement order expiry
17. Add PDF generation

---

## Testing

### Test Structure

```
backend/
└── tests/
    ├── unit/           # Service tests
    ├── integration/    # API tests
    └── conftest.py     # Fixtures
```

### Run Tests

```bash
pytest tests/
pytest --cov=backend coverage
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection |
| REDIS_URL | Redis connection |
| JWT_SECRET_KEY | Token signing key |
| STRIPE_SECRET_KEY | Stripe API key |
| RAZORPAY_KEY_ID | Razorpay key |
| SMTP_HOST | Email server |

---

## Common Issues

| Issue | Solution |
|-------|----------|
| N+1 queries | Use DataLoader |
| Slow queries | Add indexes, cache |
| Token expiry | Implement refresh |
| Webhook failures | Add retry logic |

---

## Out of Scope

- GraphQL subscriptions
- Multi-language
- Advanced caching
- WebSocket beyond basic

---

**End of Backend Spec**