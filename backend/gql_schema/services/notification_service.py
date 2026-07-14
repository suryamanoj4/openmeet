"""Notification service."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import select, update, func
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Notification


class NotificationService:
    """Service for managing user notifications."""

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get_for_user(self, user_id: UUID, unread_only: bool = False, skip: int = 0, limit: int = 50) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id, Notification.is_active == True)
        if unread_only:
            query = query.where(Notification.is_read == False)
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.exec(query)
        return list(result.all())

    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.session.exec(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False, Notification.is_active == True)
        )
        return result.one()

    async def create(
        self,
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {},
        )
        self.session.add(notif)
        await self.session.flush()
        return notif

    async def mark_read(self, notification_id: UUID) -> Optional[Notification]:
        result = await self.session.exec(
            select(Notification).where(Notification.id == notification_id)
        )
        notif = result.first()
        if not notif:
            return None
        notif.is_read = True
        notif.read_at = datetime.utcnow()
        await self.session.flush()
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.session.exec(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount