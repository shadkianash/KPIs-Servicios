import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ConflictStrategy(StrEnum):
    """Supported conflict resolution strategies."""

    SOURCE_WINS = "SOURCE_WINS"
    DATABASE_WINS = "DATABASE_WINS"
    MOST_RECENT = "MOST_RECENT"
    IGNORE = "IGNORE"


class ResolverStrategy(StrEnum):
    """Supported master data resolution strategies for missing values."""

    CREATE_IF_MISSING = "CREATE_IF_MISSING"
    REJECT_IF_MISSING = "REJECT_IF_MISSING"
    WARNING_ONLY = "WARNING_ONLY"


@dataclass(frozen=True)
class SynchronizationContext:
    """Read-only context governing a single synchronization execution."""

    import_job_id: uuid.UUID
    sync_id: uuid.UUID = field(default_factory=uuid.uuid4)
    correlation_id: str = field(default_factory=lambda: f"sync-{uuid.uuid4()}")
    conflict_strategy: ConflictStrategy = ConflictStrategy.SOURCE_WINS
    client_resolver_strategy: ResolverStrategy = ResolverStrategy.CREATE_IF_MISSING
    engineer_resolver_strategy: ResolverStrategy = ResolverStrategy.CREATE_IF_MISSING
    technology_resolver_strategy: ResolverStrategy = ResolverStrategy.CREATE_IF_MISSING
    team_resolver_strategy: ResolverStrategy = ResolverStrategy.CREATE_IF_MISSING


@dataclass
class SynchronizationResult:
    """Execution audit metrics and status outcomes of a Synchronization Job."""

    sync_id: uuid.UUID
    import_job_id: uuid.UUID
    correlation_id: str
    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    finished_at: datetime | None = None
    duration_ms: int = 0
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED

    inserted_records: int = 0
    updated_records: int = 0
    unchanged_records: int = 0
    rejected_records: int = 0

    warnings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
