"""Follower model (users following organizations)."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class FollowerBase(SQLModel):
    """Base follower fields."""

    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")


class Follower(FollowerBase, table=True):
    """Organization follower model."""

    __tablename__ = "followers"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: "User" = Relationship(back_populates="followers")
    organization: "Organization" = Relationship(back_populates="followers")

    def __repr__(self) -> str:
        return f"<Follower {self.user_id} -> {self.organization_id}>"
