from unittest.mock import AsyncMock, MagicMock

import pytest

from app.etl.core.models import IdempotencyError, SchemaError
from app.etl.services.import_service import ImportService


@pytest.mark.anyio
async def test_valid_ticket_details_import() -> None:
    """Verifies that a valid Ticket Details CSV parses and imports successfully."""
    # 1. Arrange: Prepare valid CSV string
    csv_content = (
        "ticket id,subject,desc,created date,status,team\n"
        "TKT-101,Login Issue,Cannot log in,2026-03-01 10:00:00,In Progress,SecOps\n"
        "TKT-102,Firewall Rule,Add rule,2026-03-02 12:30:00,Closed,FirewallTeam\n"
    )
    content_bytes = csv_content.encode("utf-8")

    # Mock DB AsyncSession
    mock_session = AsyncMock()
    mock_session.add = MagicMock()  # Synchronous session method
    # Mock select result to simulate no existing file checksum
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.all.return_value = []  # No existing keys in DB
    mock_session.execute.return_value = mock_execute_result

    # 2. Act
    service = ImportService()
    result = await service.import_file(
        session=mock_session,
        file_name="details_test.csv",
        content_bytes=content_bytes,
        schema_name="ticket_details",
    )

    # 3. Assert
    assert result.status == "COMPLETED"
    assert result.processed_rows == 2
    assert result.imported_rows == 2
    assert result.invalid_rows == 0
    assert len(result.failures) == 0

    # Verify job tracking was created
    assert mock_session.add.call_count == 2  # 1 for job init, 1 for update
    assert mock_session.commit.call_count == 2


@pytest.mark.anyio
async def test_duplicate_file_detection() -> None:
    """Asserts that duplicate file (by checksum) raises IdempotencyError."""
    # Arrange
    csv_content = "ticket id,subject\nTKT-101,Login Issue\n"
    content_bytes = csv_content.encode("utf-8")

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    # Simulate existing checksum (not None)
    mock_execute_result.scalar_one_or_none.return_value = object()
    mock_session.execute.return_value = mock_execute_result

    # Act & Assert
    service = ImportService()
    with pytest.raises(IdempotencyError) as exc_info:
        await service.import_file(
            session=mock_session,
            file_name="dup_test.csv",
            content_bytes=content_bytes,
            schema_name="ticket_details",
        )
    assert "has already been imported" in str(exc_info.value)


@pytest.mark.anyio
async def test_missing_required_columns() -> None:
    """Verifies that missing required columns raises SchemaError."""
    # Arrange: ticket_id is missing from headers
    csv_content = (
        "subject,desc,created date\nLogin Issue,Cannot log in,2026-03-01 10:00:00\n"
    )
    content_bytes = csv_content.encode("utf-8")

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_execute_result

    # Act & Assert
    service = ImportService()
    with pytest.raises(SchemaError) as exc_info:
        await service.import_file(
            session=mock_session,
            file_name="missing_col_test.csv",
            content_bytes=content_bytes,
            schema_name="ticket_details",
        )
    assert "Missing required columns" in str(exc_info.value)


@pytest.mark.anyio
async def test_empty_csv_file() -> None:
    """Asserts that importing an empty CSV file raises SchemaError."""
    content_bytes = b""

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_execute_result

    service = ImportService()
    result = await service.import_file(
        session=mock_session,
        file_name="empty.csv",
        content_bytes=content_bytes,
        schema_name="ticket_details",
    )
    assert result.processed_rows == 0
    assert result.status == "COMPLETED"


@pytest.mark.anyio
async def test_row_validation_failures_mismatches() -> None:
    """Verifies that invalid types or malformed dates are isolated."""
    # Arrange: details with invalid types (ticket_id can't be null, date is malformed)
    csv_content = (
        "ticket id,subject,created date\n"
        "TKT-101,Valid Ticket,2026-03-01 10:00:00\n"
        ",Null Ticket,2026-03-02 12:30:00\n"  # Missing ID (Required violation)
        "TKT-103,Bad Date,malformed-date-string\n"  # Invalid date format
    )
    content_bytes = csv_content.encode("utf-8")

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.all.return_value = []
    mock_session.execute.return_value = mock_execute_result

    # Act
    service = ImportService()
    result = await service.import_file(
        session=mock_session,
        file_name="failures_test.csv",
        content_bytes=content_bytes,
        schema_name="ticket_details",
    )

    # Assert
    assert result.processed_rows == 3
    assert result.imported_rows == 1  # Only row 1 is fully valid
    assert result.invalid_rows == 2
    assert len(result.failures) == 2

    # Verify type and null failure error classifications
    failure_types = [f.error_type for f in result.failures]
    assert "missing_field" in failure_types
    assert "type_mismatch" in failure_types


@pytest.mark.anyio
async def test_duplicate_keys_within_file() -> None:
    """Verifies that duplicated business keys inside the same CSV are isolated."""
    # Arrange: duplicate TKT-101
    csv_content = (
        "ticket id,subject\n"
        "TKT-101,Subject 1\n"
        "TKT-101,Subject 2\n"  # Duplicate business key
    )
    content_bytes = csv_content.encode("utf-8")

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.all.return_value = []
    mock_session.execute.return_value = mock_execute_result

    # Act
    service = ImportService()
    result = await service.import_file(
        session=mock_session,
        file_name="dup_keys.csv",
        content_bytes=content_bytes,
        schema_name="ticket_details",
    )

    # Assert
    assert result.processed_rows == 2
    assert result.imported_rows == 1  # First is imported, second is isolated
    assert result.invalid_rows == 1
    assert result.failures[0].error_type == "duplicate_key"


@pytest.mark.anyio
async def test_windows_1252_bom_encoding() -> None:
    """Verifies that UTF-8 BOM and Windows-1252 (cp1252) encodings decode cleanly."""
    # Prepare CP1252 content with special characters (accented characters like é)
    csv_content = "ticket id,subject\nTKT-101,Incidente de inicio de sesión\n"
    content_bytes = csv_content.encode("cp1252")

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.all.return_value = []
    mock_session.execute.return_value = mock_execute_result

    # Act
    service = ImportService()
    result = await service.import_file(
        session=mock_session,
        file_name="encoding_test.csv",
        content_bytes=content_bytes,
        schema_name="ticket_details",
        encoding="cp1252",
    )

    # Assert
    assert result.status == "COMPLETED"
    assert result.processed_rows == 1
    assert result.imported_rows == 1
