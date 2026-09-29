"""Add cosine index for document chunk embeddings.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-30

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding_hnsw", table_name="document_chunks")
