"""Audit log model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class AuditLogBase(SQLModel):
    """Base audit log fields."""

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)
    resource_type: str = Field(max_length=50)
    resource_id: Optional[uuid.UUID] = Field(default=None)
    organization_id: Optional[uuid.UUID] = Field(default=None, foreign_key="organizations.id")
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    changes: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class AuditLog(AuditLogBase, table=True):
    """Audit log model for system-wide audit trail."""

    __tablename__ = "audit_logs"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="audit_logs")
    organization: Optional["Organization"] = Relationship(back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action}>"
