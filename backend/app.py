"""FastAPI application with GraphQL."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from auth import get_auth_context
from database import AsyncSessionLocal, async_engine
from gql_schema import schema
from gql_schema.services.payment_service import PaymentService
from payment_provider import get_provider
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Welcome to OpenMeets GraphQL API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ---------- Payment webhook ----------


async def _process_webhook(
    provider_name: str,
    event_type: str,
    provider_order_id: str,
    failure_reason: Optional[str] = None,
    extra: Optional[dict] = None,
):
    session = AsyncSessionLocal()
    try:
        service = PaymentService(session)

        if event_type in ("payment.captured", "order.paid"):
            await service.mark_payment_success(provider_order_id, extra_data=extra)
        elif event_type == "payment.failed":
            await service.mark_payment_failed(
                provider_order_id, failure_reason=failure_reason, extra_data=extra
            )
        else:
            logger.warning(f"Unhandled webhook event: {event_type}")

        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("Webhook processing error")
    finally:
        await session.close()


@app.post("/webhooks/razorpay")
async def payment_webhook(request: Request):
    """Handle payment provider webhook events."""
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    provider = get_provider("razorpay")
    if not provider.verify_webhook(raw_body, signature):
        logger.warning("Webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event", "")
    entity = payload.get("payload", {})

    provider_order_id = ""
    failure_reason = None

    if "payment" in entity:
        payment_entity = entity["payment"]["entity"]
        provider_order_id = payment_entity.get("order_id", "")
        if event_type == "payment.failed":
            failure_reason = payment_entity.get("error_description")
    elif "order" in entity:
        order_entity = entity["order"]["entity"]
        provider_order_id = order_entity.get("id", "")

    logger.info(f"Webhook: {event_type} order={provider_order_id}")

    await _process_webhook(
        provider_name="razorpay",
        event_type=event_type,
        provider_order_id=provider_order_id,
        failure_reason=failure_reason,
        extra={"webhook_payload": payload},
    )
    return {"status": "ok"}

