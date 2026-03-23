"""Organization model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class OrganizationBase(SQLModel):
    """Base organization fields."""

    name: str = Field(max_length=255)
    slug: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    website_url: Optional[str] = Field(default=None, max_length=500)
    social_links: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    settings: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class Organization(OrganizationBase, table=True):
    """Organization model (multi-tenant container)."""

    __tablename__ = "organizations"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Relationships
    members: list["Member"] = Relationship(back_populates="organization", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    followers: list["Follower"] = Relationship(back_populates="organization", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    events: list["Event"] = Relationship(back_populates="organization", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    audit_logs: list["AuditLog"] = Relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.slug}>"
