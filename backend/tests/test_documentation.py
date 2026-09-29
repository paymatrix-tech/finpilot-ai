from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.documentation.loader import (
    DOCUMENTATION_DIR,
    DOCUMENT_CATEGORIES,
    load_markdown_documents,
)
from app.documentation.indexing import chunk_count
from app.documentation.seed import document_count, seed_documents


def test_documentation_dir_has_expected_markdown_files() -> None:
    files = sorted(path.name for path in DOCUMENTATION_DIR.glob("*.md"))
    assert len(files) >= 5
    assert "ach-error-codes.md" in files
    assert "retry-policy.md" in files
    assert "gateway-runbook.md" in files
    assert set(files) == set(DOCUMENT_CATEGORIES.keys())


def test_load_markdown_documents_populates_categories() -> None:
    documents = load_markdown_documents()
    assert len(documents) == len(DOCUMENT_CATEGORIES)
    by_name = {doc.name: doc for doc in documents}
    assert by_name["ach-error-codes.md"].category == "errors"
    assert "R01" in by_name["ach-error-codes.md"].content
    assert by_name["retry-policy.md"].category == "policy"
    assert "Do not retry" in by_name["retry-policy.md"].content
    assert by_name["gateway-runbook.md"].category == "gateway"
    assert "ExamplePay" in by_name["gateway-runbook.md"].content


def test_seed_documents_persists_to_database(db: Session) -> None:
    count = seed_documents(db)
    assert count == len(DOCUMENT_CATEGORIES)
    assert document_count(db) == count
    assert chunk_count(db) > 0
    missing_embeddings = db.execute(
        text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NULL")
    ).scalar_one()
    assert missing_embeddings == 0


def test_documentation_files_are_non_empty() -> None:
    for path in DOCUMENTATION_DIR.glob("*.md"):
        assert path.stat().st_size > 0, f"{path.name} is empty"
