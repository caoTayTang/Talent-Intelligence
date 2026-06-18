"""add cv screened status

Revision ID: 5916332db492
Revises: 7800f4720140
Create Date: 2026-06-18 10:02:34.502640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5916332db492'
down_revision: Union[str, Sequence[str], None] = '7800f4720140'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Báo cho PostgreSQL biết cần thêm giá trị 'cv_screened' vào enum type
    # Lệnh COMMIT; là bắt buộc vì PostgreSQL không cho phép ALTER TYPE bên trong một transaction block
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE application_status ADD VALUE 'cv_screened'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL không hỗ trợ xóa 1 giá trị khỏi Enum một cách đơn giản.
    # Thông thường, ở hàm downgrade cho Enum, người ta sẽ bỏ trống (pass) 
    # hoặc phải viết script rất phức tạp để tạo lại type mới. 
    # Để an toàn, chúng ta để pass.
    pass
