"""Notification model (user notifications)."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class NotificationBase(SQLModel):
    """Base notification fields."""

    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    notification_type: str = Field(max_length=50)
    title: str = Field(max_length=255)
    message: str
    data: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = Field(default=None)


class Notification(NotificationBase, table=True):
    """User notification model."""

    __tablename__ = "notifications"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: "User" = Relationship(back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification {self.notification_type} -> {self.user_id}>"