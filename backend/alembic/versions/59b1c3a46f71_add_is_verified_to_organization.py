"""add is_verified to organization

Revision ID: 59b1c3a46f71
Revises: a1b2c3d4e5f6
Create Date: 2026-07-29 19:34:41.514435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59b1c3a46f71'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("organizations", "is_verified", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "is_verified")
