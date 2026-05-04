"""User service for managing users."""

import uuid
from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from gql_schema.services.base import BaseService
from models import User, Member, Follower


class UserService(BaseService[User]):
    """Service for user operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.exec(select(User).where(User.email == email))
        return result.first()

    async def get_by_id(self, id: UUID) -> Optional[User]:
        result = await self.session.exec(select(User).where(User.id == id))
        return result.first()

    async def get_user_organizations(self, user_id: UUID) -> List[Member]:
        result = await self.session.exec(
            select(Member)
            .where(Member.user_id == user_id)
            .where(Member.is_active == True)
        )
        return list(result.all())

    async def get_user_followers(self, user_id: UUID) -> List[Follower]:
        result = await self.session.exec(
            select(Follower)
            .where(Follower.user_id == user_id)
            .where(Follower.is_active == True)
        )
        return list(result.all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.exec(select(User).offset(skip).limit(limit))
        return list(result.all())