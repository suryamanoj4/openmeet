"""Contract tests for ticket and checkout validation."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gql_schema.validation import CheckoutSchema, TicketDefinitionSchema


def test_ticket_definition_rejects_invalid_price_limits_and_window():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError, match="price must not be negative"):
        TicketDefinitionSchema(
            price=-1, currency="USD", quantity=10
        )
    with pytest.raises(ValidationError, match="maximum per order"):
        TicketDefinitionSchema(
            price=1, currency="USD", quantity=10, min_per_order=5, max_per_order=2
        )
    with pytest.raises(ValidationError, match="sale end"):
        TicketDefinitionSchema(
            price=1,
            currency="USD",
            quantity=10,
            sale_start=now + timedelta(days=2),
            sale_end=now + timedelta(days=1),
        )


def test_checkout_requires_positive_unique_items():
    ticket_id = uuid4()
    with pytest.raises(ValidationError, match="select at least one"):
        CheckoutSchema(items=[])
    with pytest.raises(ValidationError, match="positive"):
        CheckoutSchema(items=[{"ticket_id": ticket_id, "quantity": 0}])
    with pytest.raises(ValidationError, match="duplicate"):
        CheckoutSchema(
            items=[
                {"ticket_id": ticket_id, "quantity": 1},
                {"ticket_id": ticket_id, "quantity": 1},
            ]
        )


def test_valid_ticket_and_checkout_are_normalized():
    ticket = TicketDefinitionSchema(
        price=0, currency="usd", quantity=100, min_per_order=1, max_per_order=4
    )
    checkout = CheckoutSchema(
        items=[{"ticket_id": uuid4(), "quantity": 2}]
    )

    assert ticket.currency == "USD"
    assert checkout.items[0].quantity == 2
