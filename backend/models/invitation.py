"""Invitation model (org member invitations)."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class InvitationBase(SQLModel):
    """Base invitation fields."""

    organization_id: uuid.UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    email: str = Field(max_length=255, index=True)
    role: str = Field(default="member", max_length=20)
    status: str = Field(default=InvitationStatus.PENDING.value, max_length=20)
    token: str = Field(max_length=500, unique=True, index=True)
    invited_by: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    accepted_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    expires_at: datetime
    accepted_at: Optional[datetime] = Field(default=None)


class Invitation(InvitationBase, table=True):
    """Organization invitation model."""

    __tablename__ = "invitations"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    organization: "Organization" = Relationship(back_populates="invitations")

    def __repr__(self) -> str:
        return f"<Invitation {self.email} -> {self.organization_id} ({self.status})>"