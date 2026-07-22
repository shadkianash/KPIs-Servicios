import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.etl.core.sync_models import (
    ConflictStrategy,
    ResolverStrategy,
    SynchronizationContext,
)
from app.etl.services.synchronization_service import SynchronizationService
from app.models.operational import Ticket
from app.models.staging import (
    ImportJob,
    StagingTicketDetail,
    StagingTicketHistory,
    StagingTimeEntry,
)


@pytest.mark.anyio
async def test_successful_synchronization_pipeline() -> None:
    """Verifies a successful details, history, and time entries sync."""
    # 1. Arrange: Prepare mock staging detail, history and time entry
    import_job_id = uuid.uuid4()
    staging_detail = StagingTicketDetail(
        ticket_id="TKT-101",
        title="Test Ticket",
        description="Detail description",
        created_date=datetime.now(UTC).replace(tzinfo=None),
        status="New",
        assigned_team="SecOps",
        raw_data={"client": "Acme Corp", "engineer": "John Doe", "technology": "Nginx"},
    )
    staging_hist = StagingTicketHistory(
        history_id="HIST-01",
        ticket_id="TKT-101",
        change_date=datetime.now(UTC).replace(tzinfo=None),
        field_changed="status",
        old_value="New",
        new_value="In Progress",
    )
    staging_time = StagingTimeEntry(
        entry_id="TIME-01",
        ticket_id="TKT-101",
        user_id="john.doe",
        work_date=datetime.now(UTC).replace(tzinfo=None),
        hours_spent=2.5,
        activity_type="Investigation",
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()  # Synchronous DB session method

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()
    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")

    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,  # ImportJob select
        None,  # Team select
        None,  # Client select
        None,  # Engineer select
        None,  # Tech select
        None,  # existing Ticket select
    ]

    mock_execute.scalars().all.side_effect = [
        [staging_detail],  # StagingTicketDetail
        [staging_hist],  # StagingTicketHistory
        [staging_time],  # StagingTimeEntry
        ["TKT-101"],  # Valid Ticket ID check
        [],  # Existing History check (empty)
        [],  # Existing Time check (empty)
    ]
    mock_session.execute.return_value = mock_execute

    # 2. Act
    service = SynchronizationService()
    context = SynchronizationContext(import_job_id=import_job_id)
    result = await service.synchronize(session=mock_session, context=context)

    # 3. Assert
    assert result.status == "COMPLETED"
    assert result.inserted_records == 3  # 1 ticket, 1 history, 1 time entry
    assert result.updated_records == 0
    assert result.rejected_records == 0
    assert len(result.errors) == 0


@pytest.mark.anyio
async def test_field_level_change_detection_and_conflict() -> None:
    """Verifies that only changed fields trigger an update, respecting strategies."""
    import_job_id = uuid.uuid4()
    staging_detail = StagingTicketDetail(
        ticket_id="TKT-101",
        title="Updated Title",  # Changed from "Original Title"
        description="Same description",
        created_date=datetime.now(UTC).replace(tzinfo=None),
        status="In Progress",
        assigned_team="SecOps",
        raw_data={},  # No client/engineer/tech -> avoids sub-select queries in test
    )

    # Mock an existing ticket in the database
    existing_ticket = Ticket(
        ticket_id_archer="TKT-101",
        title="Original Title",
        description="Same description",
        status="In Progress",
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()

    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")
    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,  # ImportJob select
        None,  # Team select
        existing_ticket,  # existing Ticket select
    ]

    mock_execute.scalars().all.side_effect = [
        [staging_detail],  # StagingTicketDetail
        [],  # StagingTicketHistory
        [],  # StagingTimeEntry
        ["TKT-101"],  # valid tickets
        [],  # existing history keys
        [],  # existing time keys
    ]
    mock_session.execute.return_value = mock_execute

    # Act with SOURCE_WINS
    service = SynchronizationService()
    context = SynchronizationContext(
        import_job_id=import_job_id,
        conflict_strategy=ConflictStrategy.SOURCE_WINS,
    )
    result = await service.synchronize(session=mock_session, context=context)

    # Assert: Overwrites with staging values
    assert result.status == "COMPLETED"
    assert result.updated_records == 1
    assert result.inserted_records == 0
    assert existing_ticket.title == "Updated Title"


@pytest.mark.anyio
async def test_database_wins_ignores_conflict() -> None:
    """Verifies that DATABASE_WINS strategy retains existing DB values on conflict."""
    import_job_id = uuid.uuid4()
    staging_detail = StagingTicketDetail(
        ticket_id="TKT-101",
        title="Staging Title",
        description="Same desc",
        status="New",
        assigned_team="SecOps",
        raw_data={},
    )

    existing_ticket = Ticket(
        ticket_id_archer="TKT-101",
        title="DB Title",
        description="Same desc",
        status="New",
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()

    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")
    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,
        None,  # Team select
        existing_ticket,
    ]

    mock_execute.scalars().all.side_effect = [
        [staging_detail],
        [],
        [],
        ["TKT-101"],  # valid tickets
        [],  # existing history keys
        [],  # existing time keys
    ]
    mock_session.execute.return_value = mock_execute

    # Act with DATABASE_WINS
    service = SynchronizationService()
    context = SynchronizationContext(
        import_job_id=import_job_id,
        conflict_strategy=ConflictStrategy.DATABASE_WINS,
    )
    result = await service.synchronize(session=mock_session, context=context)

    # Assert
    assert result.status == "COMPLETED"
    assert result.updated_records == 0
    assert result.unchanged_records == 1
    assert existing_ticket.title == "DB Title"  # Unchanged!


@pytest.mark.anyio
async def test_reject_if_missing_master_data() -> None:
    """Asserts that REJECT_IF_MISSING strategy safely rejects the record."""
    import_job_id = uuid.uuid4()
    staging_detail = StagingTicketDetail(
        ticket_id="TKT-101",
        title="Staging Title",
        description="Desc",
        status="New",
        assigned_team="UnknownTeam",  # Not in cache/DB
        raw_data={},
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()

    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")
    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,
        None,  # Team select (missing)
    ]

    mock_execute.scalars().all.side_effect = [
        [staging_detail],
        [],
        [],
        [],  # valid tickets
        [],  # existing history keys
        [],  # existing time keys
    ]
    mock_session.execute.return_value = mock_execute

    # Act with REJECT_IF_MISSING
    service = SynchronizationService()
    context = SynchronizationContext(
        import_job_id=import_job_id,
        team_resolver_strategy=ResolverStrategy.REJECT_IF_MISSING,
    )
    result = await service.synchronize(session=mock_session, context=context)

    # Assert: Rejected!
    assert result.status == "COMPLETED"
    assert result.rejected_records == 1
    assert len(result.errors) == 1
    assert "Missing required Master Data reference" in result.errors[0]["message"]


@pytest.mark.anyio
async def test_referential_integrity_checks_and_orphans() -> None:
    """Verifies history logs with missing ticket ID are isolated."""
    import_job_id = uuid.uuid4()
    staging_hist = StagingTicketHistory(
        history_id="HIST-01",
        ticket_id="ORPHAN-TKT",  # Orphaned reference!
        change_date=datetime.now(UTC).replace(tzinfo=None),
        field_changed="status",
        old_value="New",
        new_value="Closed",
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()

    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")
    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,
    ]

    mock_execute.scalars().all.side_effect = [
        [],  # StagingTicketDetail
        [staging_hist],  # StagingTicketHistory
        [],  # StagingTimeEntry
        ["TKT-101"],  # "ORPHAN-TKT" is missing!
        [],  # existing history keys
        [],  # existing time keys
    ]
    mock_session.execute.return_value = mock_execute

    # Act
    service = SynchronizationService()
    context = SynchronizationContext(import_job_id=import_job_id)
    result = await service.synchronize(session=mock_session, context=context)

    # Assert
    assert result.status == "COMPLETED"
    assert result.rejected_records == 1
    assert len(result.errors) == 1
    assert "Orphaned ticket" in result.errors[0]["message"]


@pytest.mark.anyio
async def test_transactional_rollback_preserves_audit() -> None:
    """Asserts pipeline rolls back on fatal error while audit is saved."""
    import_job_id = uuid.uuid4()

    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    nested_mock = AsyncMock()
    mock_session.begin_nested.return_value = nested_mock

    mock_execute = MagicMock()
    mock_import_job = ImportJob(job_id=import_job_id, checksum_sha256="test-sum")

    # Allow the initial ImportJob query to succeed
    mock_execute.scalar_one_or_none.side_effect = [
        mock_import_job,
    ]

    # Force error when loading staging details (inside the try/except block)
    mock_execute.scalars().all.side_effect = RuntimeError("DB Connection Terminated")
    mock_session.execute.return_value = mock_execute

    # Act
    service = SynchronizationService()
    context = SynchronizationContext(import_job_id=import_job_id)

    with pytest.raises(RuntimeError):
        await service.synchronize(session=mock_session, context=context)

    # Verify rollback was called and the SyncJob record is saved as FAILED
    assert nested_mock.rollback.call_count == 1
    assert mock_session.commit.call_count == 2
    # 1 for RUNNING setup, 1 for FAILED finalize
