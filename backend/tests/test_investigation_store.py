from fastapi.testclient import TestClient

from app.models import Payment
from app.routers.investigation import get_investigation_agent
from app.schemas import InvestigationQueryResponse, ToolExecutionStep


def _fake_response(payment_id: str, question: str) -> InvestigationQueryResponse:
    return InvestigationQueryResponse(
        payment_id=payment_id,
        question=question,
        root_cause="Gateway timeout",
        confidence="medium",
        evidence=["Read timeout contacting ExamplePay"],
        recommendation="Retry with backoff",
        sources=["timeout-handling.md"],
        answer="Root cause: Gateway timeout",
        steps=[
            ToolExecutionStep(
                tool="get_payment",
                arguments={"payment_id": payment_id},
                result={"status": "FAILED"},
            )
        ],
        model="fake",
        provider="fake",
    )


def test_create_investigation_persists_and_returns_id(
    client: TestClient, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id

    class FakeAgent:
        def investigate(self, pid: str, question: str) -> InvestigationQueryResponse:
            return _fake_response(pid, question)

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    response = client.post(
        "/api/investigations",
        json={"payment_id": payment_id},
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    investigation_id = body["id"]

    get_response = client.get(f"/api/investigations/{investigation_id}")
    assert get_response.status_code == 200
    saved = get_response.json()
    assert saved["payment_id"] == payment_id
    assert saved["root_cause"] == "Gateway timeout"
    assert saved["evidence"] == ["Read timeout contacting ExamplePay"]


def test_list_payment_investigations(
    client: TestClient, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id

    class FakeAgent:
        def investigate(self, pid: str, question: str) -> InvestigationQueryResponse:
            return _fake_response(pid, question)

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    client.post("/api/investigations", json={"payment_id": payment_id})
    client.post(
        "/api/investigations",
        json={"payment_id": payment_id, "question": "Was this a timeout?"},
    )
    client.app.dependency_overrides.clear()

    list_response = client.get(f"/api/payments/{payment_id}/investigations")
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) >= 2
    assert items[0]["payment_id"] == payment_id
    assert items[0]["root_cause"] == "Gateway timeout"


def test_get_investigation_not_found(client: TestClient) -> None:
    response = client.get("/api/investigations/999999")
    assert response.status_code == 404
