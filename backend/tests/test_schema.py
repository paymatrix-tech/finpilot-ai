from sqlalchemy import inspect, text

from app.db import engine
from app.models import (
    Document,
    DocumentChunk,
    Investigation,
    Payment,
    PaymentEvent,
    PaymentLog,
)

EXPECTED_TABLES = {
    "payments",
    "payment_events",
    "payment_logs",
    "documents",
    "document_chunks",
    "investigations",
}


def test_database_connection() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1


def test_vector_extension_installed() -> None:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar_one_or_none() == "vector"


def test_core_tables_exist() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert EXPECTED_TABLES.issubset(tables)


def test_models_match_tables() -> None:
    inspector = inspect(engine)
    models = [Payment, PaymentEvent, PaymentLog, Document, DocumentChunk, Investigation]
    for model in models:
        columns = {column["name"] for column in inspector.get_columns(model.__tablename__)}
        mapped = {column.name for column in model.__table__.columns}
        assert mapped == columns, model.__tablename__
