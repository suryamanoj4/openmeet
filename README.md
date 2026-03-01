# OpenMeets Backend

Event management platform backend API built with FastAPI and PostgreSQL.

---

## About

OpenMeets is a multi-tenant event management platform that enables organizations to create, manage, and host events with integrated ticketing, payments, and attendee management.

**Key Principle:** All events are created under organizations. Users join organizations as admins or members, and organization admins can assign members to event staff roles (organizer, co-organizer, volunteer, security).

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI (Python 3.13+) |
| **Database** | PostgreSQL 15+ |
| **ORM** | SQLAlchemy 2.0 (Async) |
| **Migrations** | Alembic |
| **Authentication** | JWT + OAuth2 |
| **Cache** | Redis |
| **Task Queue** | Celery |
| **Payment** | Stripe, Razorpay |
| **Email** | SMTP (SendGrid/AWS SES) |
| **PDF** | ReportLab |

---

## Core Features

### Authentication & Users
- JWT-based authentication with refresh tokens
- Email verification and password reset
- User profile management

### Organization Management
- Multi-tenant organization system
- Admin and member roles
- Member invitations and role management
- Organization followers for notifications

### Event Management
- Full event CRUD with draft/publish workflow
- Event staff assignment from organization members
- Venue and online event support
- Event visibility controls (public, private, unlisted)

### Registration & Payments
- Ticket-based registration with payment integration
- Multiple payment providers (Stripe, Razorpay)
- Refund management
- Order and attendee tracking

### Custom Event Pages
- Drag-and-drop page builder
- Rich content blocks (schedule, speakers, sponsors)
- Custom themes and layouts
- SEO optimization

### Attendee Management
- Real-time registration analytics
- Attendee status tracking
- Bulk operations and exports
- QR code check-in system

### Bulk Email Communication
- Email campaigns to attendees
- Recipient filtering by ticket type, status
- Email templates with personalization
- Delivery analytics

### Ticketing
- Multiple ticket types per event
- Customizable ticket designs
- PDF ticket generation with QR codes
- Inventory management

## License

AGPL-3.0
