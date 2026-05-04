"""add user role and is_superuser fields

Revision ID: f8a3c9d1e2b4
Revises: 2ed7a8955b7a
Create Date: 2026-05-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f8a3c9d1e2b4'
down_revision: Union[str, None] = '2ed7a8955b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user')
    )
    op.add_column(
        'users',
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )


def downgrade() -> None:
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'role')
