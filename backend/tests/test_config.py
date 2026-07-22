from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.main import app

client = TestClient(app)


def test_settings_singleton() -> None:
    """Assert that get_settings provides cached Settings singleton instances."""
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2
    assert settings_1.PROJECT_NAME == "KPIs-Servicios"


def test_tracing_middleware_headers() -> None:
    """Verify trace middleware injects request and correlation ID headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Correlation-ID" in response.headers
    assert response.headers["X-Request-ID"] == response.headers["X-Correlation-ID"]
