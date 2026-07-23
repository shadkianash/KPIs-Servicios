import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.dependencies.db import get_db_session
from app.main import app
from app.models.analytics import DailySnapshot, KPIExecution, MonthlySnapshot
from app.models.operational import Client


def test_analytics_health_endpoint() -> None:
    """Verifies that the /analytics/health endpoint returns successful status."""
    client = TestClient(app)
    response = client.get("/api/v1/analytics/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "active"


def test_metadata_endpoints() -> None:
    """Verifies active catalog list fetches for metadata dimensions."""
    # Mock database session execution
    mock_session = AsyncMock()
    mock_execute = MagicMock()

    mock_client = Client(id=uuid.uuid4(), name="Client Acme", is_active=True)
    mock_execute.scalar_one.return_value = 1  # count select
    mock_execute.scalars().all.return_value = [mock_client]
    mock_session.execute.return_value = mock_execute

    # Set dependency override
    app.dependency_overrides[get_db_session] = lambda: mock_session

    client = TestClient(app)
    try:
        paths = [
            "/api/v1/metadata/clients",
            "/api/v1/metadata/technologies",
            "/api/v1/metadata/engineers",
            "/api/v1/metadata/teams",
        ]
        for path in paths:
            response = client.get(path)
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert len(response.json()["data"]) == 1
            assert response.json()["data"][0]["name"] is not None
            assert response.json()["pagination"]["page"] == 1
    finally:
        app.dependency_overrides.clear()


def test_kpi_executions_endpoints() -> None:
    """Verifies listing and detailed lookup of KPI executions."""
    mock_session = AsyncMock()
    mock_execute = MagicMock()

    exec_id = uuid.uuid4()
    mock_run = KPIExecution(
        execution_id=exec_id,
        execution_status="COMPLETED",
        correlation_id="corr-123",
        processed_tickets=10,
        processed_time_entries=5,
        generated_daily_snapshots=2,
        generated_monthly_snapshots=4,
    )
    mock_execute.scalar_one.return_value = 1
    mock_execute.scalars().all.return_value = [mock_run]
    mock_execute.scalar_one_or_none.return_value = mock_run
    mock_session.execute.return_value = mock_execute

    app.dependency_overrides[get_db_session] = lambda: mock_session

    client = TestClient(app)
    try:
        # 1. List runs
        response = client.get("/api/v1/kpi/executions")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["execution_status"] == "COMPLETED"

        # 2. Detail lookup
        detail_response = client.get(f"/api/v1/kpi/executions/{exec_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["data"]["execution_id"] == str(exec_id)

        # 3. Handle non-existent run
        mock_execute.scalar_one_or_none.return_value = None
        missing_response = client.get(f"/api/v1/kpi/executions/{uuid.uuid4()}")
        assert missing_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_snapshots_filtering_and_sorting() -> None:
    """Verifies Daily and Monthly snapshot listings with sort and range limits."""
    mock_session = AsyncMock()
    mock_execute = MagicMock()

    mock_daily = DailySnapshot(
        id=uuid.uuid4(),
        snapshot_date=datetime(2026, 3, 1),
        aggregation_level="engineer",
        engineer_id="ENG-1",
        execution_id=uuid.uuid4(),
        metrics={"tickets_closed": 12},
    )
    mock_execute.scalar_one.return_value = 1
    mock_execute.scalars().all.return_value = [mock_daily]
    mock_session.execute.return_value = mock_execute

    app.dependency_overrides[get_db_session] = lambda: mock_session

    client = TestClient(app)
    try:
        # Get Daily snapshots with filtering and JSONB metrics sorting
        response = client.get(
            "/api/v1/kpi/daily?start_date=2026-03-01&sort=-metrics.tickets_closed"
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["metrics"]["tickets_closed"] == 12

        # Get Monthly snapshots with year/month checks
        mock_monthly = MonthlySnapshot(
            id=uuid.uuid4(),
            year=2026,
            month=3,
            aggregation_level="client",
            client_id="CLI-1",
            execution_id=uuid.uuid4(),
            metrics={"worked_hours": 32.5},
        )
        mock_execute.scalars().all.return_value = [mock_monthly]
        response_monthly = client.get("/api/v1/kpi/monthly?year=2026&month=3")
        assert response_monthly.status_code == 200
        assert response_monthly.json()["data"][0]["metrics"]["worked_hours"] == 32.5
    finally:
        app.dependency_overrides.clear()


def test_drilldown_endpoints() -> None:
    """Verifies Daily and Monthly drilldown paths."""
    mock_session = AsyncMock()
    mock_execute = MagicMock()

    mock_daily = DailySnapshot(
        id=uuid.uuid4(),
        snapshot_date=datetime(2026, 3, 1),
        aggregation_level="engineer",
        engineer_id="ENG-1",
        execution_id=uuid.uuid4(),
        metrics={"tickets_assigned": 5},
    )
    mock_execute.scalar_one.return_value = 1
    mock_execute.scalars().all.return_value = [mock_daily]
    mock_session.execute.return_value = mock_execute

    app.dependency_overrides[get_db_session] = lambda: mock_session

    client = TestClient(app)
    try:
        # Drilldown engineer on daily snapshot type
        response = client.get("/api/v1/drilldown/engineer/ENG-1?type=daily")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["data"]) == 1

        # Invalid drilldown type parameter error
        response_err = client.get("/api/v1/drilldown/engineer/ENG-1?type=invalid")
        assert response_err.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_openapi_schema_generation() -> None:
    """Verifies that the FastAPI OpenAPI documentation is generated correctly."""
    client = TestClient(app)
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]

    # Assert core stable contract paths are cleanly registered
    assert "/api/v1/analytics/health" in paths
    assert "/api/v1/metadata/clients" in paths
    assert "/api/v1/kpi/executions" in paths
    assert "/api/v1/kpi/daily" in paths
    assert "/api/v1/drilldown/engineer/{engineer_id}" in paths
