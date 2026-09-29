import pytest
from sqlalchemy.orm import Session

from app.documentation.seed import seed_documents
from app.repositories.documentation import DocumentationRepository
from app.tools.documentation import DocumentationTools
from app.tools.exceptions import ToolError
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools
from app.repositories.payment import PaymentRepository


@pytest.fixture
def documentation_tools(db: Session) -> DocumentationTools:
    seed_documents(db)
    return DocumentationTools(DocumentationRepository(db))


def test_search_payment_docs_finds_retry_policy(documentation_tools: DocumentationTools) -> None:
    results = documentation_tools.search_payment_docs("gateway timeout retry backoff policy")
    assert results
    assert any("retry" in result.content.lower() for result in results)
    assert all(result.source.document_name.endswith(".md") for result in results)
    assert all(result.source.document_id > 0 for result in results)
    assert all(0.0 <= result.similarity <= 1.0 for result in results)


def test_search_payment_docs_includes_source_references(
    documentation_tools: DocumentationTools,
) -> None:
    results = documentation_tools.search_payment_docs("ACH R01 insufficient funds", limit=3)
    assert len(results) <= 3
    first = results[0]
    assert first.source.document_name
    assert first.source.category
    assert first.chunk_id > 0
    assert first.source.chunk_index is not None


def test_semantic_search_ranks_closer_match_higher(documentation_tools: DocumentationTools) -> None:
    results = documentation_tools.search_payment_docs("card decline fraud do not retry")
    assert len(results) >= 2
    similarities = [result.similarity for result in results]
    assert similarities == sorted(similarities, reverse=True)


def test_search_payment_docs_requires_query(documentation_tools: DocumentationTools) -> None:
    with pytest.raises(ToolError):
        documentation_tools.search_payment_docs("   ")


def test_executor_runs_search_payment_docs(
    db: Session, documentation_tools: DocumentationTools
) -> None:
    payment_tools = PaymentTools(PaymentRepository(db))
    executor = PaymentToolExecutor(payment_tools, documentation_tools)
    payload = executor.execute("search_payment_docs", {"query": "ExamplePay gateway unavailable"})
    assert isinstance(payload, list)
    assert payload
    assert payload[0]["source"]["document_name"]
