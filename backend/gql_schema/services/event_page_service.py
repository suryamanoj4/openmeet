"""Event page service — manages custom page builder blocks for events."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import EventPage


class EventPageService:
    """Service for managing event custom pages."""

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get_by_event(self, event_id: UUID) -> Optional[EventPage]:
        result = await self.session.exec(
            select(EventPage).where(EventPage.event_id == event_id, EventPage.is_active == True)
        )
        return result.first()

    async def get_or_create(self, event_id: UUID) -> EventPage:
        page = await self.get_by_event(event_id)
        if page:
            return page
        page = EventPage(event_id=event_id, blocks=[])
        self.session.add(page)
        await self.session.flush()
        return page

    async def update_blocks(self, event_id: UUID, blocks: list) -> EventPage:
        page = await self.get_or_create(event_id)
        page.blocks = blocks
        page.updated_at = datetime.utcnow()
        await self.session.flush()
        return page

    async def publish(self, event_id: UUID) -> EventPage:
        page = await self.get_or_create(event_id)
        page.is_published = True
        page.published_at = datetime.utcnow()
        await self.session.flush()
        return page

    async def unpublish(self, event_id: UUID) -> EventPage:
        page = await self.get_by_event(event_id)
        if not page:
            page = EventPage(event_id=event_id, blocks=[])
            self.session.add(page)
            await self.session.flush()
        page.is_published = False
        page.published_at = None
        await self.session.flush()
        return page