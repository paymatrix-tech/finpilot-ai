from fastapi.testclient import TestClient

from app.models import Payment
from app.routers.investigation import get_investigation_agent


def test_investigation_rejects_missing_payment_before_agent(
    client: TestClient, sample_payments: list[Payment]
) -> None:
    agent_called = False

    class FakeAgent:
        def investigate(self, pid: str, question: str):
            nonlocal agent_called
            agent_called = True
            raise AssertionError("agent should not run for missing payment")

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    response = client.post(
        "/api/investigations",
        json={"payment_id": "PAY-DOES-NOT-EXIST", "question": "Why failed?"},
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "payment_not_found"
    assert agent_called is False


def test_investigation_llm_failure_returns_structured_error(
    client: TestClient, sample_payments: list[Payment]
) -> None:
    from app.llm.exceptions import LLMRequestError

    payment_id = sample_payments[0].id

    class FailingAgent:
        def investigate(self, pid: str, question: str):
            raise LLMRequestError("upstream timeout")

    client.app.dependency_overrides[get_investigation_agent] = lambda: FailingAgent()
    response = client.post(
        "/api/investigations",
        json={"payment_id": payment_id, "question": "Why failed?"},
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "llm_request_failed"
