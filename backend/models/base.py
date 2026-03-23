"""Base model with common fields."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields.

    All models inherit:
    - id: UUID primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - is_active: Soft delete flag
    """

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
    )
    is_active: bool = Field(
        default=True,
    )
