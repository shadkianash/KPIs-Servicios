import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KPIExecution(Base):
    """Execution metadata and audit ledger for the KPI Analytics Engine."""

    __tablename__ = "kpi_executions"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_status: Mapped[str] = mapped_column(
        String(20), default="RUNNING", nullable=False
    )  # RUNNING, COMPLETED, FAILED
    calculation_version: Mapped[str] = mapped_column(
        String(20), default="1.0.0", nullable=False
    )
    engine_version: Mapped[str] = mapped_column(
        String(20), default="1.0.0", nullable=False
    )

    # Ingestion stats
    processed_tickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_time_entries: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    generated_daily_snapshots: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    generated_monthly_snapshots: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    warnings: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    errors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_import_job_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    execution_parameters: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )


class DailySnapshot(Base):
    """Daily aggregated KPI values stored in a flexible schema."""

    __tablename__ = "daily_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    aggregation_level: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # engineer, client, technology, team, global

    # Analytical dimensional attributes
    engineer_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    client_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    technology_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    team_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    snapshot_version: Mapped[str] = mapped_column(
        String(20), default="1.0.0", nullable=False
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kpi_executions.execution_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core JSON KPI values Map
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class MonthlySnapshot(Base):
    """Monthly aggregated KPI values stored in a flexible schema."""

    __tablename__ = "monthly_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    aggregation_level: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # engineer, client, technology, team, global

    # Analytical dimensional attributes
    engineer_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    client_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    technology_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    team_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    snapshot_version: Mapped[str] = mapped_column(
        String(20), default="1.0.0", nullable=False
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kpi_executions.execution_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core JSON KPI values Map
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
