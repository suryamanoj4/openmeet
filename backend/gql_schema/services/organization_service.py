"""Organization service for managing organizations, members, and followers."""

import uuid
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from strawberry import Info

from gql_schema.services.base import BaseService
from models import Organization, Member, Event, Follower, User


class OrganizationService(BaseService[Organization]):
    """Service for organization operations."""

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.session.exec(
            select(Organization).where(Organization.slug == slug)
        )
        return result.first()

    async def get_by_id(self, id: UUID) -> Optional[Organization]:
        result = await self.session.exec(
            select(Organization).where(Organization.id == id)
        )
        return result.first()

    async def get_members(
        self,
        organization_id: UUID,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Member]:
        query = select(Member).where(
            Member.organization_id == organization_id,
            Member.is_active == True,
        )
        if role:
            query = query.where(Member.role == role)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def get_member(self, organization_id: UUID, user_id: UUID) -> Optional[Member]:
        result = await self.session.exec(
            select(Member).where(
                Member.organization_id == organization_id,
                Member.user_id == user_id,
                Member.is_active == True,
            )
        )
        return result.first()

    async def add_member(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str = "member",
    ) -> Member:
        """Add a user as member to organization."""
        existing = await self.get_member(organization_id, user_id)
        if existing:
            raise ValueError("User is already a member")

        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        member = Member(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            joined_at=datetime.utcnow(),
        )
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def update_member_role(
        self,
        organization_id: UUID,
        user_id: UUID,
        new_role: str,
    ) -> Member:
        """Update member's role."""
        member = await self.get_member(organization_id, user_id)
        if not member:
            raise ValueError("Member not found")

        member.role = new_role
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def remove_member(self, organization_id: UUID, user_id: UUID) -> bool:
        """Soft delete a member."""
        member = await self.get_member(organization_id, user_id)
        if not member:
            return False

        member.is_active = False
        await self.session.flush()
        return True

    async def get_followers(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Follower]:
        result = await self.session.exec(
            select(Follower)
            .where(Follower.organization_id == organization_id)
            .where(Follower.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    async def get_follower(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> Optional[Follower]:
        result = await self.session.exec(
            select(Follower).where(
                Follower.organization_id == organization_id,
                Follower.user_id == user_id,
                Follower.is_active == True,
            )
        )
        return result.first()

    async def add_follower(self, organization_id: UUID, user_id: UUID) -> Follower:
        """Add a user as follower."""
        existing = await self.get_follower(organization_id, user_id)
        if existing:
            return existing

        follower = Follower(
            user_id=user_id,
            organization_id=organization_id,
        )
        self.session.add(follower)
        await self.session.flush()
        await self.session.refresh(follower)
        return follower

    async def remove_follower(self, organization_id: UUID, user_id: UUID) -> bool:
        """Soft delete a follower."""
        follower = await self.get_follower(organization_id, user_id)
        if not follower:
            return False

        follower.is_active = False
        await self.session.flush()
        return True

    async def get_events(
        self,
        organization_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        query = select(Event).where(
            Event.organization_id == organization_id,
            Event.is_active == True,
        )
        if status:
            query = query.where(Event.status == status)
        result = await self.session.exec(query.offset(skip).limit(limit))
        return list(result.all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Organization]:
        result = await self.session.exec(
            select(Organization).offset(skip).limit(limit)
        )
        return list(result.all())