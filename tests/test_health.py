from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_versioned_health() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "api_version": "v1"}


def test_root_dashboard_is_available() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Gati Shram" in response.text
    assert "DEMO DATA" in response.text
