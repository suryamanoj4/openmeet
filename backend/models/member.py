"""Member model (organization membership)."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class MemberBase(SQLModel):
    """Base member fields."""

    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    role: str = Field(default="member", max_length=50)
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class Member(MemberBase, table=True):
    """Organization membership model."""

    __tablename__ = "members"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Relationships
    user: "User" = Relationship(back_populates="members")
    organization: "Organization" = Relationship(back_populates="members")

    def __repr__(self) -> str:
        return f"<Member {self.user_id} in {self.organization_id}>"
