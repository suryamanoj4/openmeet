# OpenMeets Backend - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Clients                        │
│         (Web App, Mobile App, Admin Dashboard)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / CDN                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway / Reverse Proxy                │
│                         (Nginx/Traefik)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Application Server                  │
│                        (Uvicorn/Gunicorn)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes (REST)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Access Layer (SQLAlchemy)           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │ PostgreSQL │  │   Redis    │  │   Celery   │
       │  Database  │  │   Cache    │  │   Worker   │
       └────────────┘  └────────────┘  └────────────┘
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                       ┌────────────┐  ┌────────────┐  ┌────────────┐
                       │    Email   │  │    PDF     │  │  Payment   │
                       │   Tasks    │  │  Tasks     │  │   Tasks    │
                       └────────────┘  └────────────┘  └────────────┘
```

---

## Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Framework** | FastAPI | 0.109+ |
| **Language** | Python | 3.13+ |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 2.0+ (Async) |
| **Migrations** | Alembic | 1.13+ |
| **Authentication** | JWT (python-jose) | - |
| **Password Hashing** | bcrypt (passlib) | - |
| **Cache** | Redis | 7+ |
| **Task Queue** | Celery | 5.3+ |
| **Validation** | Pydantic | 2.5+ |
| **Email** | aiosmtplib | 3.0+ |
| **PDF Generation** | ReportLab | 4.0+ |
| **QR Code** | qrcode | 7.4+ |
| **Payments** | Stripe SDK | 7.0+ |
| **HTTP Client** | httpx | 0.26+ |
| **Logging** | structlog | 24.1+ |
| **Rate Limiting** | slowapi | 0.1.9+ |

---

## Why Not Keycloak?

**Decision: Use FastAPI + JWT instead of Keycloak**

### Rationale:
1. **Simpler Architecture** - One less service to deploy, maintain, and monitor
2. **Custom RBAC Needs** - Organization/event hierarchy is easier to implement directly
3. **Faster Development** - No Keycloak configuration, realms, or identity brokering setup
4. **Full Control** - Complete control over auth flows, token structure, and session management
5. **Single Application** - Keycloak shines with multiple apps sharing auth (not our case initially)
6. **Team Expertise** - Easier for team to understand and modify custom auth vs. Keycloak black box

### When to Reconsider Keycloak:
- Multiple applications requiring SSO
- Enterprise clients demanding SAML/OIDC federation
- Dedicated DevOps team for Keycloak maintenance
- Complex identity provider integrations needed

### Our Auth Approach:
- JWT access tokens (15 min expiry)
- Refresh tokens with database revocation (7 day expiry)
- Custom role-based access control (RBAC)
- Organization and event-level permissions
- Session management with concurrent session limits

---

## Repository Structure

```
openmeets-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory & startup
│   ├── config.py               # Pydantic settings (env vars)
│   ├── database.py             # DB connection & session factory
│   │
│   ├── core/                   # Core utilities (shared across app)
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, password hashing, OAuth2
│   │   ├── permissions.py      # RBAC decorators & helpers
│   │   ├── exceptions.py       # Custom exceptions & handlers
│   │   └── dependencies.py     # Common FastAPI dependencies
│   │
│   ├── models/                 # SQLAlchemy ORM models (DB tables)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── audit.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── auth.py
│   │
│   ├── api/                    # REST API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py             # Route-specific dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Aggregates all v1 routers
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── organizations.py
│   │       ├── events.py
│   │       ├── tickets.py
│   │       ├── orders.py
│   │       ├── payments.py
│   │       └── staff.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organization.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── email.py
│   │   └── pdf_generator.py
│   │
│   ├── tasks/                  # Celery async tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── email_tasks.py
│   │   ├── payment_tasks.py
│   │   └── pdf_tasks.py
│   │
│   └── utils/                  # Helper utilities
│       ├── __init__.py
│       ├── smtp.py
│       ├── payment_gateway.py
│       └── qr_generator.py
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures & config
│   ├── factories/              # Test data factories
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
│
├── docs/
│   ├── ARCHITECTURE.md         # This file
│   ├── FEATURES.md             # Feature list
│   ├── API.md                  # API documentation
│   └── DEPLOYMENT.md           # Deployment guide
│
├── docker-compose.yml          # Local development orchestration
├── Dockerfile                  # Production container image
├── pyproject.toml              # Python dependencies & tooling
└── README.md                   # Project overview
```

---

## Layer Architecture

### 1. API Layer (`app/api/`)
- HTTP request/response handling
- Input validation (Pydantic schemas)
- Authentication & authorization checks
- Response formatting
- Error handling
- **No business logic** - delegates to services

### 2. Service Layer (`app/services/`)
- Business logic implementation
- Transaction management
- External service integration (email, payment, PDF)
- Domain rules enforcement
- **No HTTP-specific code** - pure Python

### 3. Data Access Layer (`app/models/`)
- Database schema definition
- ORM mappings
- Query helpers
- Relationships definition

### 4. Core Layer (`app/core/`)
- Cross-cutting concerns
- Security utilities
- Permission system
- Common dependencies
- Exception handlers

---

## Database Design Principles

### Multi-Tenancy Strategy

**Organization-based isolation:**
- Every resource belongs to an organization
- Users access resources via organization membership
- Queries filtered by organization context

```python
# Example: Event query always includes org filter
events = await db.execute(
    select(Event)
    .where(Event.organization_id == current_org_id)
    .where(Event.is_active == true)
)
```

### Soft Deletes

**All critical tables use soft deletes:**
- `is_active` boolean flag
- Deleted records retained for audit
- Queries filter `is_active = true`

### Audit Fields

**All tables include:**
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp
- `created_by` - User who created (optional)

### UUIDs as Primary Keys

**All tables use UUID:**
- Prevents ID enumeration attacks
- Distributed ID generation friendly
- Better for data replication

---

## Authentication Flow

### Registration Flow
```
User → POST /auth/register → Validate → Hash Password → Create User
       → Generate Verification Token → Send Email → Return Success
```

### Login Flow
```
User → POST /auth/login → Validate Credentials → Generate Tokens
       → Store Refresh Token Hash → Return Access + Refresh Tokens
```

### Token Refresh Flow
```
Client → POST /auth/refresh (with refresh token) → Validate Token
         → Generate New Access Token → (Optionally rotate refresh token)
         → Return New Access Token
```

### Protected Request Flow
```
Client → Request + Access Token → API Endpoint
         → Extract Token → Validate Signature → Check Expiry
         → Load User → Check Permissions → Execute Handler
```

---

## Authorization Model

### Role Hierarchy

```
Organization Level:
  owner > admin > member > viewer

Event Level:
  organizer > co-organizer > volunteer > security
```

### Permission Check Flow

```python
# 1. Extract organization from request
org_id = request.path_params.get("organization_id")

# 2. Get user's role in organization
membership = await get_membership(user_id, org_id)

# 3. Check if role has required permission
if not has_permission(membership.role, "events:create"):
    raise HTTPException(403, "Insufficient permissions")
```

### Permission Matrix

| Resource | Action | Owner | Admin | Member | Viewer |
|----------|--------|-------|-------|--------|--------|
| Organization | Update | ✓ | ✓ | ✗ | ✗ |
| Organization | Delete | ✓ | ✗ | ✗ | ✗ |
| Members | Invite | ✓ | ✓ | ✗ | ✗ |
| Members | Remove | ✓ | ✓ | ✗ | ✗ |
| Events | Create | ✓ | ✓ | ✓ | ✗ |
| Events | View All | ✓ | ✓ | ✓ | ✓ |
| Events | Manage Own | ✓ | ✓ | ✓ | ✗ |
| Events | Manage All | ✓ | ✓ | ✗ | ✗ |
| Tickets | Manage | ✓ | ✓ | ✓* | ✗ |
| Orders | View | ✓ | ✓ | ✓* | ✗ |
| Reports | View | ✓ | ✓ | ✓ | ✓ |

*Own events only

---

## API Design Patterns

### RESTful Conventions

| HTTP Method | Endpoint | Description |
|-------------|----------|-------------|
| GET | `/api/v1/events` | List events |
| POST | `/api/v1/events` | Create event |
| GET | `/api/v1/events/{id}` | Get event |
| PUT | `/api/v1/events/{id}` | Update event |
| DELETE | `/api/v1/events/{id}` | Delete event |

### Nested Resources

```
GET /api/v1/organizations/{id}/events
GET /api/v1/events/{id}/ticket-types
GET /api/v1/events/{id}/staff
GET /api/v1/orders/{id}/payments
```

### Response Format

**Success:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [...]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Paginated:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

---

## Caching Strategy

### What to Cache

| Data | TTL | Reason |
|------|-----|--------|
| User profile | 5 min | Frequently accessed, rarely changes |
| Organization details | 10 min | Shared across many requests |
| Event details | 5 min | Read-heavy, changes infrequently |
| Ticket types | 2 min | Changes during sales |
| Public event pages | 1 min | High traffic, can be slightly stale |

### Cache Invalidation

```python
# Invalidate on update
async def update_event(event_id, data):
    await db.update(Event, event_id, data)
    await cache.delete(f"event:{event_id}")
    await cache.delete(f"org:{org_id}:events")
```

### Cache-Aside Pattern

```python
async def get_event(event_id):
    # Try cache first
    cached = await cache.get(f"event:{event_id}")
    if cached:
        return cached
    
    # Fallback to database
    event = await db.get(Event, event_id)
    
    # Populate cache
    await cache.set(f"event:{event_id}", event, ttl=300)
    
    return event
```

---

## Task Queue Architecture

### Celery Configuration

```python
# High-priority queue (time-sensitive)
CELERY_QUEUES = {
    "high": {
        "tasks": [
            "send_payment_confirmation",
            "process_refund"
        ]
    },
    "default": {
        "tasks": [
            "send_ticket_email",
            "generate_ticket_pdf"
        ]
    },
    "low": {
        "tasks": [
            "send_event_reminder",
            "cleanup_expired_orders"
        ]
    }
}
```

### Task Retry Strategy

```python
@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email_id):
    try:
        send_email(email_id)
    except Exception as e:
        # Exponential backoff: 60s, 120s, 240s
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
```

### Scheduled Tasks

```python
CELERY_BEAT_SCHEDULE = {
    "release-expired-tickets": {
        "task": "tasks.order_tasks.release_expired_tickets",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "send-event-reminders": {
        "task": "tasks.email_tasks.send_event_reminders",
        "schedule": crontab(minute="0", hour="*/6"),  # Every 6 hours
    },
    "cleanup-old-audit-logs": {
        "task": "tasks.maintenance_tasks.cleanup_audit_logs",
        "schedule": crontab(minute="0", hour="3"),  # Daily at 3 AM
    },
}
```

---

## Security Architecture

### Password Security

- **Hashing Algorithm:** bcrypt (cost factor 12)
- **Salt:** Auto-generated per password
- **Storage:** Only hash stored, never plain text

### JWT Security

```python
# Access Token
{
    "sub": "user-uuid",
    "email": "user@example.com",
    "type": "access",
    "exp": 1234567890,
    "iat": 1234567800
}

# Security Measures:
# - Short expiry (15 minutes)
# - Signature verification (HS256)
# - Expiry validation on every request
# - No sensitive data in payload
```

### Input Validation

- All inputs validated via Pydantic schemas
- Type coercion and validation
- String length limits
- Regex patterns for structured data
- Custom validators for business rules

### SQL Injection Prevention

- SQLAlchemy ORM for all queries
- Parameterized queries (no string interpolation)
- No raw SQL in application code

### XSS Prevention

- JSON responses only (no HTML from API)
- Output encoding handled by frontend
- CORS configured for specific origins

### CSRF Protection

- JWT in Authorization header (not cookies)
- Refresh tokens in HTTP-only cookies
- SameSite cookie attribute

---

## Error Handling

### Exception Hierarchy

```python
class AppException(Exception):
    """Base exception"""

class AuthenticationError(AppException):
    """Invalid credentials"""

class AuthorizationError(AppException):
    """Insufficient permissions"""

class NotFoundError(AppException):
    """Resource not found"""

class ValidationError(AppException):
    """Invalid input data"""

class ConflictError(AppException):
    """Resource conflict (duplicate, etc.)"""
```

### Exception Handlers

```python
@app.exception_handler(ValidationError)
async def validation_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}}
    )

@app.exception_handler(AuthorizationError)
async def authz_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={"error": {"code": "FORBIDDEN", "message": "Access denied"}}
    )
```

---

## Logging Strategy

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Usage
logger.info(
    "order_created",
    order_id=str(order.id),
    user_id=str(user.id),
    total=float(order.total_amount),
    event_id=str(event.id)
)
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging info |
| INFO | Normal operations (requests, tasks) |
| WARNING | Recoverable issues |
| ERROR | Errors requiring attention |
| CRITICAL | System-wide failures |

### Log Context

Every log includes:
- Timestamp
- Log level
- Event name
- Request ID (for tracing)
- User ID (if authenticated)
- Organization ID (if applicable)

---

## Testing Strategy

### Test Pyramid

```
           /\
          /  \      E2E Tests (10%)
         /----\     Critical user journeys
        /      \
       /--------\   Integration Tests (30%)
      /          \  API + Database
     /------------\
    /              \ Unit Tests (60%)
   /                \Services, validators, utils
  /__________________\
```

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── factories/            # Factory Boy factories
│   ├── user.py
│   ├── organization.py
│   └── event.py
├── unit/                 # Unit tests
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Integration tests
│   ├── test_auth.py
│   ├── test_events.py
│   └── test_orders.py
└── e2e/                  # E2E tests
    └── test_user_journey.py
```

### Test Fixtures

```python
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_user():
    return UserFactory()

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

---

## Deployment Architecture

### Development

```yaml
# docker-compose.yml
services:
  api:      # FastAPI (hot reload)
  worker:   # Celery worker
  db:       # PostgreSQL
  redis:    # Redis
```

### Production

```
┌─────────────────────────────────────────┐
│           Load Balancer                 │
│         (AWS ALB / Nginx)               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │  API 1  │ │  API 2  │ │  API 3  │
   │(Uvicorn)│ │(Uvicorn)│ │(Uvicorn)│
   └─────────┘ └─────────┘ └─────────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │   DB    │ │  Redis  │ │  Celery │
   │(Primary)│ │ Cluster │ │ Workers │
   └─────────┘ └─────────┘ └─────────┘
```

### Environment Variables

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=<secure-random-string>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/openmeets

# Redis
REDIS_URL=redis://host:6379/0

# JWT
JWT_SECRET=<secure-random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@openmeets.com

# Payment
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
FRONTEND_URL=https://app.openmeets.com
ALLOWED_ORIGINS=https://app.openmeets.com,https://admin.openmeets.com
```

---

## API Versioning

### Strategy: URL Versioning

```
/api/v1/...   # Current stable version
/api/v2/...   # Future version (when needed)
```

### Deprecation Policy

1. **Announcement:** 3 months notice before sunset
2. **Documentation:** Deprecation notice in docs
3. **Response Headers:** `Deprecation: true` header
4. **Migration Guide:** Provide migration documentation

---

## Performance Considerations

### Database Optimization

- Indexes on foreign keys
- Indexes on frequently queried columns
- Composite indexes for common query patterns
- Query optimization via EXPLAIN ANALYZE
- Connection pooling (asyncpg)

### Caching

- Redis for frequently accessed data
- Cache-aside pattern
- Cache invalidation on writes
- TTL-based expiration

### Async Operations

- All I/O operations async (database, HTTP, Redis)
- Celery for long-running tasks (email, PDF)
- Non-blocking request handling

### Pagination

- Cursor-based pagination for large datasets
- Default page size: 20
- Maximum page size: 100
- Pagination metadata in response

---

## Monitoring & Observability

### Health Checks

```python
GET /health
{
    "status": "healthy",
    "database": "healthy",
    "redis": "healthy",
    "version": "0.1.0"
}
```

### Metrics to Track

- Request latency (p50, p95, p99)
- Request rate (requests/second)
- Error rate (errors/second)
- Database query time
- Cache hit rate
- Task queue size
- Active connections

### Alerting

- API error rate > 1%
- Response time p99 > 2s
- Database connection pool exhausted
- Celery task failures
- Disk space < 20%

---

## Future Considerations

### Scalability Options

1. **Horizontal Scaling:** Add more API instances behind load balancer
2. **Database Read Replicas:** For read-heavy workloads
3. **Database Sharding:** By organization for multi-tenancy at scale
4. **Service Extraction:** Extract payment, email, PDF as microservices if needed

### Feature Extensions

- Mobile app backend (same API)
- Admin dashboard API
- Public API for third-party integrations
- Webhook system for event notifications
- GraphQL API (in addition to REST)
- Real-time features (WebSockets for live updates)
