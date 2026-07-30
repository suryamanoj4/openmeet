"""Validation schemas for ticket configuration and checkout requests."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class TicketDefinitionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: float
    currency: str
    quantity: int
    min_per_order: int = 1
    max_per_order: int = 10
    sale_start: datetime | None = None
    sale_end: datetime | None = None

    @field_validator("price")
    @classmethod
    def non_negative_price(cls, value: float) -> float:
        if value < 0:
            raise ValueError("price must not be negative")
        return value

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, value: str) -> str:
        value = value.upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("currency must be a three-letter code")
        return value

    @field_validator("quantity")
    @classmethod
    def non_negative_quantity(cls, value: int) -> int:
        if value < 0:
            raise ValueError("quantity must not be negative")
        return value

    @model_validator(mode="after")
    def valid_limits_and_window(self) -> "TicketDefinitionSchema":
        if self.min_per_order < 1:
            raise ValueError("minimum per order must be at least one")
        if self.max_per_order < self.min_per_order:
            raise ValueError("maximum per order must not be below the minimum")
        if self.sale_start and self.sale_end and self.sale_end <= self.sale_start:
            raise ValueError("ticket sale end must be after sale start")
        return self


class CheckoutItemSchema(BaseModel):
    ticket_id: UUID
    quantity: int

    @field_validator("quantity")
    @classmethod
    def positive_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ticket quantity must be positive")
        return value


class CheckoutSchema(BaseModel):
    items: list[CheckoutItemSchema]

    @model_validator(mode="after")
    def non_empty_unique_items(self) -> "CheckoutSchema":
        if not self.items:
            raise ValueError("select at least one ticket")
        ticket_ids = [item.ticket_id for item in self.items]
        if len(ticket_ids) != len(set(ticket_ids)):
            raise ValueError("duplicate ticket selections are not allowed")
        return self
