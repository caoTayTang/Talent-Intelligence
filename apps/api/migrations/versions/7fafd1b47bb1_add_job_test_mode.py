"""add job test mode

Revision ID: 7fafd1b47bb1
Revises: 6be302d65b1a
Create Date: 2026-08-17 18:25:34.155861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7fafd1b47bb1'
down_revision: Union[str, Sequence[str], None] = '6be302d65b1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    test_mode_enum = sa.Enum("fixed", "generated", "hybrid", name="test_mode")
    test_mode_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('jobs', sa.Column('dynamic_test_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('jobs', sa.Column('test_duration', sa.Integer(), server_default="3", nullable=False))
    op.add_column('jobs', sa.Column('test_mode', test_mode_enum, nullable=True))
    op.alter_column("jobs", "test_duration", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'test_mode')
    op.drop_column('jobs', 'test_duration')
    op.drop_column('jobs', 'dynamic_test_config')
    test_mode_enum = sa.Enum("fixed", "generated", "hybrid", name="test_mode")
    test_mode_enum.drop(op.get_bind(), checkfirst=True)
