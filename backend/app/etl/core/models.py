import datetime as dt
import uuid
from dataclasses import dataclass, field


class ETLError(Exception):
    """Base exception for all ETL-related errors."""


class SchemaError(ETLError):
    """Raised when schema validation fails or columns are missing."""


class IdempotencyError(ETLError):
    """Raised when a file has already been imported (checksum duplicate)."""


@dataclass(frozen=True)
class ImportContext:
    """Read-only context for an ETL import execution batch."""

    correlation_id: str
    import_batch_id: uuid.UUID = field(default_factory=uuid.uuid4)
    source_system: str = "Archer"
    connector_name: str = "CSVConnector"
    started_at: dt.datetime = field(
        default_factory=lambda: dt.datetime.now(dt.UTC).replace(tzinfo=None)
    )


@dataclass(frozen=True)
class ValidationFailure:
    """Detailed metadata about a validation error in a record."""

    row_index: int
    field_name: str
    error_type: str  # e.g., missing_field, type_mismatch, invalid_format, duplicate_key
    message: str
    raw_value: str | None = None


@dataclass
class ImportResult:
    """Audit metrics and execution statistics for an import job."""

    job_id: uuid.UUID
    import_batch_id: uuid.UUID
    file_name: str
    original_file_name: str
    checksum_sha256: str
    started_at: dt.datetime
    finished_at: dt.datetime | None = None
    duration_ms: int = 0
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    error_message: str | None = None

    # Processing indicators
    processed_rows: int = 0
    imported_rows: int = 0
    updated_rows: int = 0
    skipped_rows: int = 0
    duplicated_rows: int = 0
    invalid_rows: int = 0

    # Validation failures captured
    failures: list[ValidationFailure] = field(default_factory=list)
