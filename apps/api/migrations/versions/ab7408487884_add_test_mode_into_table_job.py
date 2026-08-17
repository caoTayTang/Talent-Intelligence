"""add test_mode into table job

Revision ID: ab7408487884
Revises: 5916332db492
Create Date: 2026-08-17 19:03:22.661472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab7408487884'
down_revision: Union[str, Sequence[str], None] = '5916332db492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Yêu cầu PostgreSQL tạo Type Enum này trước
    test_mode_enum = sa.Enum('fixed', 'generated', 'hybrid', name='test_mode')
    test_mode_enum.create(op.get_bind(), checkfirst=True)
    
    # 2. Sau đó mới add column bằng cái type vừa tạo
    op.add_column('jobs', sa.Column('test_mode', test_mode_enum, nullable=True))


def downgrade() -> None:
    # 1. Rollback thì xóa column trước
    op.drop_column('jobs', 'test_mode')
    
    # 2. Sau đó xóa luôn Type Enum trong CSDL
    test_mode_enum = sa.Enum('fixed', 'generated', 'hybrid', name='test_mode')
    test_mode_enum.drop(op.get_bind(), checkfirst=True)
