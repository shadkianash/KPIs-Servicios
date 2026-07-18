from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoints() -> None:
    """Verifies that all health endpoints return HTTP 200 and the correct payload."""
    paths = ["/health", "/api/health", "/api/v1/health"]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "KPIs Servicios API",
            "version": "0.1.0",
        }
