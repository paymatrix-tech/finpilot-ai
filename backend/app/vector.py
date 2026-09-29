"""pgvector configuration shared by schema and RAG indexing."""

from sqlalchemy import text
from sqlalchemy.engine import Engine

EMBEDDING_DIMENSIONS = 1536


def ensure_pgvector_extension(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()


def pgvector_available(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            ).first()
        return row is not None
    except Exception:
        return False
