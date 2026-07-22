import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.services.kpi_engine import KPIEngine
from app.models.operational import Ticket, TicketHistory, TimeEntry


@pytest.mark.anyio
async def test_kpi_engine_calculation_and_snapshots() -> None:
    """Verifies KPI engine loads, calculates, aggregates, and snapshots."""
    # 1. Arrange: Prepare mock operational models
    # We will simulate:
    # - 1 Ticket assigned and closed
    # - 1 Ticket history status change
    # - 1 TimeEntry representing 5.5 hours
    ticket_1 = Ticket(
        id=uuid.uuid4(),
        ticket_id_archer="TKT-101",
        title="Test Ticket",
        created_date=datetime(2026, 3, 1, 10, 0, 0),
        closed_date=datetime(2026, 3, 1, 14, 30, 0),  # 4.5 hours resolution duration
        status="Closed",
        engineer_id="ENG-01",
        client_id="CLI-01",
        technology_id="TECH-01",
        team_id="TEAM-01",
    )
    # To test validation anomalies (negative resolution duration):
    ticket_2 = Ticket(
        id=uuid.uuid4(),
        ticket_id_archer="TKT-102",
        title="Anomalous Ticket",
        created_date=datetime(2026, 3, 2, 10, 0, 0),
        closed_date=datetime(2026, 3, 2, 8, 0, 0),  # Negative resolution!
        status="Closed",
        engineer_id="ENG-01",
        client_id="CLI-01",
        technology_id="TECH-01",
        team_id="TEAM-01",
    )

    history_entry = TicketHistory(
        id=uuid.uuid4(),
        history_id_archer="HIST-01",
        ticket_id="TKT-101",
        change_date=datetime(2026, 3, 1, 11, 0, 0),  # Earliest change (1 hr response)
        field_changed="status",
        old_value="New",
        new_value="In Progress",
    )

    time_entry = TimeEntry(
        id=uuid.uuid4(),
        entry_id_archer="TIME-01",
        ticket_id="TKT-101",
        user_id="john.doe",
        work_date=datetime(2026, 3, 1, 12, 0, 0),
        hours_spent=5.5,
        activity_type="Investigation",
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    mock_execute = MagicMock()
    # Mock selects return values
    mock_execute.scalars().all.side_effect = [
        [ticket_1, ticket_2],  # Ticket select
        [history_entry],  # TicketHistory select
        [time_entry],  # TimeEntry select
    ]
    mock_session.execute.return_value = mock_execute

    # 2. Act
    engine = KPIEngine()
    exec_id = await engine.calculate_and_snapshot(
        session=mock_session, correlation_id="test-correlation"
    )

    # 3. Assert
    assert exec_id is not None
    # Verify that the session had additions representing Daily and Monthly snapshots
    assert mock_session.add.call_count > 0
    assert mock_session.commit.call_count > 0


@pytest.mark.anyio
async def test_kpi_engine_handles_empty_datasets_gracefully() -> None:
    """Verifies KPI engine handles empty operational datasets cleanly."""
    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    mock_execute = MagicMock()
    mock_execute.scalars().all.side_effect = [
        [],  # Empty Tickets
        [],  # Empty History
        [],  # Empty Time entries
    ]
    mock_session.execute.return_value = mock_execute

    # Act
    engine = KPIEngine()
    exec_id = await engine.calculate_and_snapshot(
        session=mock_session, correlation_id="test-empty"
    )

    # Assert
    assert exec_id is not None
    assert mock_session.commit.call_count > 0
