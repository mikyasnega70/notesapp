"""add new column in notes

Revision ID: e7a80f6f624c
Revises: 7ddcb5ab5234
Create Date: 2026-02-12 09:15:18.994560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a80f6f624c'
down_revision: Union[str, Sequence[str], None] = '7ddcb5ab5234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notes', sa.Column('owner_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
