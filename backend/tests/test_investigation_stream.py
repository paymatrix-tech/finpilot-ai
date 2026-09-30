import json

from fastapi.testclient import TestClient

from app.models import Payment
from app.routers.investigation import get_investigation_agent
from app.schemas import InvestigationQueryResponse, ToolExecutionStep


def test_investigation_stream_emits_tool_and_complete_events(
    client: TestClient, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id

    class FakeAgent:
        def investigate_with_events(self, pid: str, question: str):
            yield "started", {"payment_id": pid, "question": question}
            step = ToolExecutionStep(
                tool="get_payment",
                arguments={"payment_id": pid},
                result={"status": "FAILED", "error_code": "R01"},
            )
            yield "tool_step", step.model_dump(mode="json")
            yield "rca_started", {}
            response = InvestigationQueryResponse(
                payment_id=pid,
                question=question,
                root_cause="Insufficient funds",
                confidence="high",
                evidence=["Gateway returned R01"],
                recommendation="Do not retry",
                sources=["ach-error-codes.md"],
                answer="Root cause: Insufficient funds",
                steps=[step],
                model="fake",
                provider="fake",
                insufficient_evidence=False,
            )
            yield "complete", json.loads(response.model_dump_json())

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    with client.stream(
        "POST",
        "/api/investigations/stream",
        json={"payment_id": payment_id, "question": "Why failed?"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        chunks = list(response.iter_text())
    client.app.dependency_overrides.clear()

    body = "".join(chunks)
    assert "event: started" in body
    assert "event: tool_step" in body
    assert "event: rca_started" in body
    assert "event: complete" in body
    assert '"root_cause": "Insufficient funds"' in body
    assert '"id":' in body
