# OpenMeets

Event management platform built with Svelte, TypeScript, FastAPI, and GraphQL.

## What It Is

Multi-tenant event management platform enabling organizations to create, manage, and host events with:
- Custom event pages (drag-drop builder)
- Ticket sales with inventory management
- Payment processing (Stripe, Razorpay)
- Attendee check-in with QR codes
- Bulk email communication
- Analytics and reporting

## Quick Start

### Backend

```bash
cd backend
uv sync
uv run main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/SPEC.md](docs/SPEC.md) | What to build (product) |
| [docs/TODO.md](docs/TODO.md) | Development status |
| [backend/docs/SPEC.md](backend/docs/SPEC.md) | Backend guide |
| [frontend/docs/SPEC.md](frontend/docs/SPEC.md) | Frontend guide |

## Architecture

```
openmeet/
├── backend/     # FastAPI + GraphQL (Strawberry)
├── frontend/    # Svelte + TypeScript
└── docs/        # Documentation
```

## Key Files

| Path | Description |
|------|-------------|
| backend/main.py | Server entry |
| backend/gql_schema/ | GraphQL API |
| backend/models/ | Database models |
| frontend/src/routes/ | Pages |
| frontend/src/lib/components/ | UI components |

## Tech Stack

- Frontend: Svelte, TypeScript, TailwindCSS, Urql
- Backend: FastAPI, Python 3.13+, PostgreSQL, SQLAlchemy 2.0
- GraphQL: Strawberry

License: AGPL-3.0