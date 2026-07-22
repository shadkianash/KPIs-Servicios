import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ImportJob(Base):
    """Auditing and idempotency tracking of each import execution."""

    __tablename__ = "import_jobs"

    job_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    import_batch_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, index=True)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_name: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Process indicators and metrics
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    imported_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status: RUNNING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(20), default="RUNNING", nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    importer_version: Mapped[str] = mapped_column(
        String(20), default="0.1.0", nullable=False
    )
    correlation_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)


class StagingTicketDetail(Base):
    """Staging table that preserves raw details from Ticket Details CSV."""

    __tablename__ = "staging_ticket_details"

    staging_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Raw imported fields from the CSV
    ticket_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    assigned_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Traceability fields
    synchronized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class StagingTicketHistory(Base):
    """Staging table that preserves raw details from Ticket History CSV."""

    __tablename__ = "staging_ticket_history"

    staging_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Raw imported fields from the CSV
    history_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    change_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    field_changed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(String, nullable=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Traceability fields
    synchronized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class StagingTimeEntry(Base):
    """Staging table that preserves raw details from Time Entries CSV."""

    __tablename__ = "staging_time_entries"

    staging_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Raw imported fields from the CSV
    entry_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    work_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hours_spent: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Traceability fields
    synchronized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
