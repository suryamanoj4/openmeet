"""Email log model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class EmailLogBase(SQLModel):
    """Base email log fields."""

    recipient_email: str = Field(max_length=255)
    template_name: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="pending", max_length=50)
    error_message: Optional[str] = Field(default=None)
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class EmailLog(EmailLogBase, table=True):
    """Email delivery tracking model."""

    __tablename__ = "email_logs"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    def __repr__(self) -> str:
        return f"<EmailLog {self.recipient_email} - {self.status}>"
