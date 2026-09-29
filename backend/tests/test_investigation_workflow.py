from sqlalchemy.orm import Session

from app.documentation.seed import seed_documents
from app.llm.stub import StubLLMClient
from app.models import Payment
from app.repositories.documentation import DocumentationRepository
from app.repositories.payment import PaymentRepository
from app.services.investigation_agent import InvestigationAgent
from app.tools.documentation import DocumentationTools
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools


def test_stub_investigation_workflow_returns_structured_rca(
    db: Session, sample_payments: list[Payment]
) -> None:
    seed_documents(db)
    payment_id = sample_payments[0].id
    payment_tools = PaymentTools(PaymentRepository(db))
    documentation_tools = DocumentationTools(DocumentationRepository(db))
    agent = InvestigationAgent(
        StubLLMClient(),
        PaymentToolExecutor(payment_tools, documentation_tools),
    )

    result = agent.investigate(payment_id, "Why did this payment fail?")

    assert result.payment_id == payment_id
    assert result.root_cause == "Insufficient funds"
    assert result.confidence == "high"
    assert result.steps[0].tool == "get_payment"
    assert result.recommendation
    assert result.sources


def test_create_investigation_endpoint(
    client, sample_payments: list[Payment], monkeypatch
) -> None:
    from fastapi.testclient import TestClient

    from app.routers.investigation import get_investigation_agent

    assert isinstance(client, TestClient)
    payment_id = sample_payments[0].id

    class FakeAgent:
        def investigate(self, pid: str, question: str):
            from app.schemas import InvestigationQueryResponse, ToolExecutionStep

            return InvestigationQueryResponse(
                payment_id=pid,
                question=question,
                root_cause="Gateway timeout",
                confidence="medium",
                evidence=["Read timeout contacting ExamplePay"],
                recommendation="Retry with backoff",
                sources=["timeout-handling.md"],
                answer="Root cause: Gateway timeout",
                steps=[
                    ToolExecutionStep(
                        tool="search_payment_docs",
                        arguments={"query": "timeout"},
                        result=[],
                    )
                ],
                model="fake",
                provider="fake",
            )

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    response = client.post(
        "/api/investigations",
        json={"payment_id": payment_id},
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["root_cause"] == "Gateway timeout"
    assert body["question"] == "Why did this payment fail?"
