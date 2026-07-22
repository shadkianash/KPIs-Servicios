import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Client(Base):
    """Client operational dimensional entity."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )


class Engineer(Base):
    """Engineer/Consultant operational dimensional entity."""

    __tablename__ = "engineers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )


class Technology(Base):
    """Technology operational dimensional entity."""

    __tablename__ = "technologies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )


class Team(Base):
    """Team/Queue operational dimensional entity."""

    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )


class Ticket(Base):
    """Primary operational entity representing a Service Ticket."""

    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id_archer: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Master Data Relationships
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    engineer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("engineers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    technology_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("technologies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )


class TicketHistory(Base):
    """Audit logs/changes associated with Service Tickets."""

    __tablename__ = "ticket_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    history_id_archer: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.ticket_id_archer", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    change_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    field_changed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(String, nullable=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)


class TimeEntry(Base):
    """Worked hours recorded on Service Tickets."""

    __tablename__ = "time_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id_archer: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.ticket_id_archer", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    work_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hours_spent: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)


class SyncJob(Base):
    """Tracks the execution and results of each synchronization execution."""

    __tablename__ = "sync_jobs"

    sync_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    import_job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ingestion metrics
    inserted_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unchanged_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Audit & Log fields
    warnings: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    errors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="RUNNING", nullable=False
    )  # RUNNING, COMPLETED, FAILED
    correlation_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
