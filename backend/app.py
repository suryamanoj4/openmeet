"""FastAPI application with GraphQL."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from strawberry.fastapi import GraphQLRouter

from auth import get_auth_context
from config import settings
from database import AsyncSessionLocal, async_engine
from gql_schema import schema
from gql_schema.services.payment_service import PaymentService
from tasks import scheduler

logger = logging.getLogger("openmeets")


async def get_context(
    request: Request,
) -> dict:
    session = AsyncSessionLocal()
    authorization = request.headers.get("Authorization")

    context = {"db": session, "current_user": None, "request": request}

    if authorization:
        auth_ctx = await get_auth_context(session, authorization)
        if auth_ctx:
            context["current_user"] = auth_ctx

    return context


async def get_root_value():
    return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("OpenMeets API starting")
    await scheduler.start()
    yield
    await scheduler.stop()
    await async_engine.dispose()
    logger.info("OpenMeets API shut down")


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    root_value_getter=get_root_value,
    allow_queries_via_get=True,
)

app = FastAPI(
    title="OpenMeets API",
    description="GraphQL API for OpenMeets event management platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Welcome to OpenMeets GraphQL API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ---------- Payment webhook endpoints ----------


async def _handle_webhook_event(
    provider: str,
    event_type: str,
    provider_payment_id: str,
    extra: Optional[dict] = None,
    failure_reason: Optional[str] = None,
):
    session = AsyncSessionLocal()
    try:
        service = PaymentService(session)

        if event_type in ("payment_intent.succeeded", "payment.captured", "order.paid"):
            await service.mark_payment_success(provider_payment_id, extra_data=extra)
        elif event_type in ("payment_intent.payment_failed", "payment.failed"):
            await service.mark_payment_failed(provider_payment_id, failure_reason=failure_reason, extra_data=extra)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type} from {provider}")

        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Webhook processing error: {e}")
        raise
    finally:
        await session.close()


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.json()
    event_type = payload.get("type", "")

    data = payload.get("data", {}).get("object", {})
    provider_payment_id = data.get("id", "")
    amount = data.get("amount", 0)
    currency = data.get("currency", "usd")

    logger.info(f"Stripe webhook: {event_type} payment={provider_payment_id}")

    await _handle_webhook_event(
        provider="stripe",
        event_type=event_type,
        provider_payment_id=provider_payment_id,
        extra={"stripe_event": payload},
    )
    return {"status": "ok"}


@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    """Handle Razorpay webhook events."""
    payload = await request.json()
    event_type = payload.get("event", "")

    payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})
    provider_payment_id = payment_data.get("id", "")
    amount = payment_data.get("amount", 0)
    currency = payment_data.get("currency", "INR")

    # Map Razorpay event names
    event_map = {
        "payment.captured": "payment.captured",
        "payment.failed": "payment.failed",
        "order.paid": "order.paid",
    }
    mapped_event = event_map.get(event_type, event_type)

    logger.info(f"Razorpay webhook: {event_type} payment={provider_payment_id}")

    failure_reason = payment_data.get("error_description") if event_type == "payment.failed" else None

    await _handle_webhook_event(
        provider="razorpay",
        event_type=mapped_event,
        provider_payment_id=provider_payment_id,
        extra={"razorpay_event": payload},
        failure_reason=failure_reason,
    )
    return {"status": "ok"}

