from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Verifies that GET /health returns HTTP 200 and the specified payload."""
    for path in ["/health", "/api/health"]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "KPIs Servicios API",
            "version": "0.1.0",
        }
