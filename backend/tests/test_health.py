from fastapi.testclient import TestClient

from backend.app.main import AI_DISCLAIMER, app

client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_carries_disclaimer() -> None:
    # Safety rule 2: AI output is always labelled. Guard the constant from day one.
    assert client.get("/health").json()["disclaimer"] == AI_DISCLAIMER
