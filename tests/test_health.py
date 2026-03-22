from fastapi.testclient import TestClient

from signaldesk.main import app

client = TestClient(app)


def test_health_returns_200_json() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
