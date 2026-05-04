import uuid
from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class TicketType:
    id: uuid.UUID
    event_id: uuid.UUID
    name: str
    description: Optional[str]
    price: float
    currency: str
    quantity: int
    sold_quantity: int
    min_per_order: int
    max_per_order: int
    sale_start: Optional[datetime]
    sale_end: Optional[datetime]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
