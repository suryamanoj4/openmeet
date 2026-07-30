"""separate payment IDs and make attendee creation idempotent

Revision ID: c7e9a3d4b5f6
Revises: 59b1c3a46f71
Create Date: 2026-07-30 15:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7e9a3d4b5f6"
down_revision: Union[str, None] = "59b1c3a46f71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("provider_order_id", sa.String(length=255), nullable=True),
    )
    op.execute(
        "UPDATE payments SET provider_order_id = provider_payment_id "
        "WHERE provider_order_id IS NULL"
    )
    op.alter_column("payments", "provider_order_id", nullable=False)
    op.create_index(
        "ix_payments_provider_order_id",
        "payments",
        ["provider_order_id"],
        unique=True,
    )
    op.alter_column(
        "payments",
        "provider_payment_id",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.add_column(
        "attendees",
        sa.Column("sequence_number", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY order_item_id ORDER BY created_at, id
                ) - 1 AS sequence_number
            FROM attendees
        )
        UPDATE attendees
        SET sequence_number = ranked.sequence_number
        FROM ranked
        WHERE attendees.id = ranked.id
        """
    )
    op.alter_column("attendees", "sequence_number", nullable=False)
    op.create_unique_constraint(
        "uq_attendees_order_item_sequence",
        "attendees",
        ["order_item_id", "sequence_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_attendees_order_item_sequence",
        "attendees",
        type_="unique",
    )
    op.drop_column("attendees", "sequence_number")

    op.execute(
        "UPDATE payments SET provider_payment_id = provider_order_id "
        "WHERE provider_payment_id IS NULL"
    )
    op.alter_column(
        "payments",
        "provider_payment_id",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.drop_index("ix_payments_provider_order_id", table_name="payments")
    op.drop_column("payments", "provider_order_id")
