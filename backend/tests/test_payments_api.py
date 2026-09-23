from fastapi.testclient import TestClient

from app.models import Payment


def test_list_payments_includes_seeded_rows(client: TestClient, sample_payments: list[Payment]) -> None:
    response = client.get("/api/payments", params={"q": "PAY-TEST-"})
    assert response.status_code == 200
    payload = response.json()
    ids = {item["id"] for item in payload["items"]}
    assert {payment.id for payment in sample_payments} <= ids


def test_list_payments_filters_by_status(client: TestClient, sample_payments: list[Payment]) -> None:
    response = client.get("/api/payments", params={"q": "PAY-TEST-", "status": "FAILED"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["id"] for item in items] == ["PAY-TEST-1001"]
    assert items[0]["error_code"] == "R01"
    assert sample_payments[0].status == "FAILED"


def test_get_payment_returns_details(client: TestClient, sample_payments: list[Payment]) -> None:
    payment_id = sample_payments[0].id
    response = client.get(f"/api/payments/{payment_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == payment_id
    assert body["amount"] == "2450.00"
    assert body["gateway"] == "ExamplePay"


def test_get_payment_not_found(client: TestClient) -> None:
    response = client.get("/api/payments/PAY-DOES-NOT-EXIST")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_payment_events(client: TestClient, sample_payments: list[Payment]) -> None:
    payment_id = sample_payments[0].id
    response = client.get(f"/api/payments/{payment_id}/events")
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["event_type"] for item in items] == [
        "PAYMENT_CREATED",
        "VALIDATED",
        "GATEWAY_RESPONSE",
    ]
    assert items[-1]["metadata"]["error_code"] == "R01"


def test_list_payment_logs(client: TestClient, sample_payments: list[Payment]) -> None:
    payment_id = sample_payments[0].id
    response = client.get(f"/api/payments/{payment_id}/logs")
    assert response.status_code == 200
    messages = [item["message"] for item in response.json()["items"]]
    assert messages == [
        "Sending payment to gateway",
        "Gateway returned R01",
    ]


def test_list_payment_events_not_found(client: TestClient) -> None:
    response = client.get("/api/payments/PAY-MISSING/events")
    assert response.status_code == 404
