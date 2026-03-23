"""Refresh token model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class RefreshTokenBase(SQLModel):
    """Base refresh token fields."""

    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    token_hash: str = Field(unique=True, index=True, max_length=255)
    expires_at: datetime
    revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = Field(default=None)
    created_ip: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)


class RefreshToken(RefreshTokenBase, table=True):
    """JWT refresh token storage model."""

    __tablename__ = "refresh_tokens"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: "User" = Relationship(back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken {self.token_hash[:10]}...>"
