"""Background task scheduler for periodic maintenance jobs."""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlmodel import select, delete

from database import AsyncSessionLocal
from models import Order, RefreshToken

logger = logging.getLogger("openmeets.tasks")


async def expire_pending_orders():
    """Cancel orders that have been pending beyond their expiry time."""
    session = AsyncSessionLocal()
    try:
        now = datetime.utcnow()
        result = await session.exec(
            select(Order).where(
                Order.status == "pending",
                Order.expires_at <= now,
            )
        )
        expired_orders = list(result.all())

        count = 0
        for order in expired_orders:
            for item in order.items:
                ticket = await session.get(type(item.ticket), item.ticket_id)
                if ticket:
                    ticket.sold_quantity = max(0, ticket.sold_quantity - item.quantity)

            order.status = "cancelled"
            order.payment_status = "cancelled"
            order.cancelled_at = now
            count += 1

        await session.commit()
        if count > 0:
            logger.info(f"Expired {count} pending orders")
    except Exception:
        await session.rollback()
        logger.exception("Error expiring pending orders")
    finally:
        await session.close()


async def cleanup_expired_tokens():
    """Remove expired or revoked refresh tokens older than 30 days."""
    session = AsyncSessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        result = await session.exec(
            delete(RefreshToken).where(
                RefreshToken.expires_at < cutoff,
                RefreshToken.revoked == True,
            )
        )
        deleted = result.rowcount
        await session.commit()
        if deleted:
            logger.info(f"Cleaned up {deleted} expired refresh tokens")
    except Exception:
        await session.rollback()
        logger.exception("Error cleaning up refresh tokens")
    finally:
        await session.close()


class TaskScheduler:
    """Simple background task scheduler using asyncio."""

    def __init__(self):
        self._tasks: list[asyncio.Task] = []
        self._running = False

    def add_interval_task(self, coro_fn, interval_seconds: float, name: str = ""):
        async def _runner():
            while self._running:
                try:
                    await coro_fn()
                except Exception:
                    logger.exception(f"Task '{name}' failed")
                await asyncio.sleep(interval_seconds)

        self._tasks.append(asyncio.create_task(_runner()))
        logger.info(f"Scheduled task '{name}' every {interval_seconds}s")

    async def start(self):
        logger.info("Task scheduler starting")
        self._running = True

        # Run these periodic tasks
        self.add_interval_task(expire_pending_orders, interval_seconds=60, name="expire_pending_orders")
        self.add_interval_task(cleanup_expired_tokens, interval_seconds=3600, name="cleanup_expired_tokens")

    async def stop(self):
        logger.info("Task scheduler stopping")
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Task scheduler stopped")


scheduler = TaskScheduler()
