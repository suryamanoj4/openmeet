"""Event page model (custom page builder blocks)."""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


class EventPageBase(SQLModel):
    """Base event page fields."""

    event_id: uuid.UUID = Field(foreign_key="events.id", ondelete="CASCADE", index=True)
    blocks: list = Field(default_factory=list, sa_column=Column(JSONB))
    is_published: bool = Field(default=False)
    published_at: Optional[datetime] = Field(default=None)


class EventPage(EventPageBase, table=True):
    """Event custom page builder model — stores ordered drag-and-drop blocks as JSON."""

    __tablename__ = "event_pages"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    event: "Event" = Relationship(back_populates="pages")

    def __repr__(self) -> str:
        return f"<EventPage event={self.event_id} blocks={len(self.blocks)}>"