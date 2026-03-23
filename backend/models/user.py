"""User model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    """Base user fields."""

    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    is_email_verified: bool = Field(default=False)


class User(UserBase, table=True):
    """User account model."""

    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Relationships
    members: list["Member"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    followers: list["Follower"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    orders: list["Order"] = Relationship(back_populates="creator", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
