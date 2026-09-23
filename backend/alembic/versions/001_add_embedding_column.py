"""Add embedding column to documents table for semantic search.

Revision ID: 001_add_embedding_column
Revises:
Create Date: 2026-09-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "001_add_embedding_column"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add nullable 'embedding' LargeBinary column to documents table."""
    op.add_column(
        "documents",
        sa.Column("embedding", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    """Remove 'embedding' column from documents table."""
    op.drop_column("documents", "embedding")
