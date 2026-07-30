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

Copy `.env.example` to `.env` and set the database values. The checked-in
defaults are for local development only.

### Backend

```bash
cd backend
uv sync
DEBUG=true uv run main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Production

Production runs behind the included nginx reverse proxy:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Before starting it:

- set `JWT_SECRET_KEY` to a long, unique secret; the backend refuses to start
  in non-debug mode with its built-in default
- set `CORS_ORIGINS` to a comma-separated list of the exact public frontend
  origins, for example `https://events.example.com`
- set `FRONTEND_URL` to the public application URL so email links are correct
- configure the PostgreSQL and payment-provider secrets
- leave `PUBLIC_GRAPHQL_URL` unset so browsers use nginx at same-origin
  `/graphql`; set it during the frontend build only when the API has a
  different public origin

The production frontend uses the committed Node adapter and lockfile. Backend
and frontend health checks gate nginx startup.

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
