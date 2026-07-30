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

The complete production-shaped local stack starts with one command:

```bash
docker compose up
```

Open `http://localhost:8080`. The first startup:

- creates PostgreSQL storage
- applies every Alembic migration
- starts the FastAPI backend and adapter-node frontend
- exposes both through nginx

Normal startup never creates users or sample data. Later starts preserve the
database and reapply only outstanding migrations.

No `.env` file is required for this local stack. Copy `.env.example` to
`.env` only when you want to override its defaults.

### Demo data

Sample accounts, organizations, and events are explicitly opt-in:

```bash
docker compose --profile demo up
```

The demo administrator is `admin@openmeet.local` with password `password123`.
The seed runs only when the database contains no users and safely skips later
runs. Never enable the `demo` profile against a production database.

### Create the first production administrator

After normal startup, bootstrap the first administrator with credentials
supplied directly to the one-off command:

```bash
docker compose run --rm \
  -e ADMIN_EMAIL=admin@example.com \
  -e ADMIN_PASSWORD='replace-with-a-strong-secret' \
  backend python bootstrap_admin.py
```

The password must contain at least 12 characters. Optional
`ADMIN_FIRST_NAME` and `ADMIN_LAST_NAME` values default to `Platform` and
`Administrator`. Rerunning the command for the same superuser is safe and does
not rotate its password. The command refuses to elevate an existing ordinary
account with the supplied email address.

### Common Docker commands

```bash
docker compose up --build       # rebuild after dependency or source changes
docker compose logs -f          # follow all service logs
docker compose ps               # inspect health and one-shot service results
docker compose down             # stop while preserving PostgreSQL data
docker compose down --volumes   # stop and permanently reset local data
```

Only nginx is published to the host, on `127.0.0.1:8080` by default. Override
`APP_BIND_ADDRESS` or `APP_PORT` in `.env` when needed. PostgreSQL, the backend,
and the frontend remain private to the Compose network.

`docker-compose.prod.yml` remains as a compatibility alias, but plain
`docker compose up` is the canonical command.

## Runtime Configuration

Before using the stack beyond local evaluation:

- set `JWT_SECRET_KEY` to a long, unique secret; the backend refuses to start
  with its built-in application default, while Compose supplies a
  local-demo-only fallback
- set `COMPOSE_CORS_ORIGINS` to the exact public frontend origins
- set `COMPOSE_FRONTEND_URL` to the public application URL so redirects and
  email links are correct
- configure the PostgreSQL and payment-provider secrets

Browsers use nginx at same-origin `/graphql`. Process liveness is available at
`/health/live` and database readiness at `/health/ready`. Compose gates
migrations, backend, frontend, and nginx on the relevant completion or health
condition. Demo seeding is a separate opt-in one-shot service.

Plain startup is safe from automatic demo-account creation. Internet-facing
deployments must still replace all Compose defaults, use external secret
management, terminate TLS, and avoid enabling the `demo` profile.

### Running without Docker

Backend:

```bash
cd backend
uv sync
DEBUG=true uv run main.py
```

Frontend:

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
├── Dockerfile   # Backend and frontend image targets
├── backend/     # FastAPI + GraphQL (Strawberry)
├── frontend/    # Svelte + TypeScript
├── nginx/       # Same-origin reverse proxy
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
