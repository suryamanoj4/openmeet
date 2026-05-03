# OpenMeets - Developer Specification

**Purpose:** Explain what this project is AND guide developers on what to build

---

## What This Project Is

OpenMeets is a multi-tenant event management platform that enables organizations to create, manage, and host events with integrated ticketing, payments, and attendee management.

**Key Features:**
- Event creation and management with custom pages (drag-drop builder)
- Ticket sales with inventory management
- Payment processing (Stripe, Razorpay)
- Attendee check-in with QR codes
- Bulk email communication
- Analytics and reporting

**Why Build This:**
- Third-party platforms charge 5-15% commission
- Limited customization on existing platforms
- No direct access to attendee data
- Need full control over branding and data

---

## Architecture

```
openmeet/
├── backend/     # FastAPI + Strawberry GraphQL
├── frontend/    # Svelte + TypeScript
└── docs/        # Documentation
```

**Technology Stack:**
- Frontend: Svelte, TypeScript, TailwindCSS, Urql
- Backend: FastAPI, Python 3.13+, PostgreSQL, Redis, Celery
- GraphQL: Strawberry
- ORM: SQLAlchemy 2.0 (Async)

---

## Data Model

### Core Entities

| Entity | Description | Key Fields |
|--------|-------------|------------|
| User | Platform users | email, password_hash, profile |
| Organization | Event hosts | name, slug, members, followers |
| Event | Managed events | name, dates, venue, tickets |
| Ticket | Ticket types | price, quantity, sale dates |
| Order | Purchases | customer, items, payment_status |
| Attendee | Ticket holders | check_in_status, QR code |
| Payment | Transactions | provider, amount, status |

### Relationships

```
User → Member → Organization → Event → Ticket → Order → Attendee
                              ↓          ↓
                           Staff     Payment
```

---

## Core Features to Build

### Phase 1: Foundation

1. **Authentication**
   - User registration + login
   - JWT tokens (access + refresh)
   - Password reset

2. **Organizations**
   - Create/organize events
   - Add/manage members
   - Organization followers

3. **Events**
   - Create/edit events
   - Event types (conference, workshop, meetup, webinar)
   - Status workflow (draft → published → completed)
   - Visibility (public, private, unlisted)

### Phase 2: Ticketing & Payments

4. **Tickets**
   - Multiple ticket types per event
   - Pricing and inventory
   - Sale date windows

5. **Orders**
   - Cart and checkout
   - Order expiry (15 min)
   - Order confirmation

6. **Payments**
   - Stripe integration
   - Razorpay integration
   - Refund processing

### Phase 3: Attendee Experience

7. **Public Event Pages**
   - Event details display
   - Ticket selection
   - Payment flow

8. **Attendee Management**
   - Attendee list
   - Search and filter
   - Export

9. **Check-in**
   - QR code scanning
   - Manual check-in
   - Check-in stats

### Phase 4: Communication

10. **Page Builder**
    - Drag-drop components
    - Theme customization
    - Preview (desktop/mobile)

11. **Email**
    - Bulk email campaigns
    - Templates
    - Analytics

12. **Notifications**
    - In-app notifications
    - Event reminders

---

## User Roles

| Role | Permissions |
|------|-------------|
| User | Register, follow orgs, buy tickets |
| Org Member | View events, assigned as staff |
| Org Admin | Create events, manage members |
| Event Organizer | Full event control |
| Volunteer | Check-in attendees |
| Security | Scan QR codes only |

---

## Development Priority

### High Priority
1. User auth (register, login, tokens)
2. Organization CRUD
3. Event CRUD
4. Ticket types
5. Order + checkout
6. Payments
7. Public event pages

### Medium Priority
8. Page builder
9. Attendee list
10. Check-in system
11. Email campaigns

### Lower Priority
12. Analytics
13. Notifications
14. Advanced features

---

## Getting Started

### Backend

```bash
cd backend
# Install dependencies
uv sync

# Run database migrations
alembic upgrade head

# Start server
uv run main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## API Design

GraphQL-first API. Example queries:

```graphql
# Fetch event with tickets
query GetEvent($id: UUID!) {
  event(id: $id) {
    name
    tickets { name, price, available }
  }
}

# Create order
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) { orderNumber, totalAmount }
}
```

---

## Database

PostgreSQL 15+ with SQLAlchemy 2.0 (async).

All tables include:
- `id` (UUID, PK)
- `is_active` (soft delete)
- `created_at`, `updated_at`
- `created_by` (FK, optional)

---

## Out of Scope (v1.0)

- Mobile apps
- Live streaming
- Multi-language
- White-labeling
- Social features
- Advanced analytics

---

**End of Spec**