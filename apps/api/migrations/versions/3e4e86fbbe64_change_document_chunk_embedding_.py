"""change document chunk embedding dimension

Revision ID: 3e4e86fbbe64
Revises: 38289d6e6f86
Create Date: 2026-06-07 22:30:30.236793

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3e4e86fbbe64"
down_revision: Union[str, Sequence[str], None] = "38289d6e6f86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Resize document chunk embeddings for Scaleway qwen3-embedding-8b."""
    op.execute("DELETE FROM document_chunks")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(4096) "
        "USING embedding::vector(4096)"
    )


def downgrade() -> None:
    """Restore the previous 2048-dimensional embedding column."""
    op.execute("DELETE FROM document_chunks")
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(2048) "
        "USING embedding::vector(2048)"
    )

