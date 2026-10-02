from fastapi.testclient import TestClient


def test_health_reports_ok_when_database_is_up(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "finpilot-api"
    assert body["status"] == "ok"
    assert body["database"] == "up"
