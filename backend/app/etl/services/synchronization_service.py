import logging
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.etl.core.sync_models import (
    ConflictStrategy,
    ResolverStrategy,
    SynchronizationContext,
    SynchronizationResult,
)
from app.etl.services.master_data_resolver import MasterDataResolver
from app.etl.utils.change_detector import ChangeDetector
from app.models.operational import SyncJob, Ticket, TicketHistory, TimeEntry
from app.models.staging import (
    ImportJob,
    StagingTicketDetail,
    StagingTicketHistory,
    StagingTimeEntry,
)

logger = logging.getLogger(__name__)


class SynchronizationService:
    """Orchestrates production operational model synchronization."""

    def __init__(self) -> None:
        self.change_detector = ChangeDetector()

    async def synchronize(
        self, session: AsyncSession, context: SynchronizationContext
    ) -> SynchronizationResult:
        """Executes the complete transactional data synchronization pipeline."""
        start_time_ns = time.perf_counter_ns()
        resolver = MasterDataResolver()

        # Initialize the Result stats
        result = SynchronizationResult(
            sync_id=context.sync_id,
            import_job_id=context.import_job_id,
            correlation_id=context.correlation_id,
        )

        logger.info(
            f"[{context.correlation_id}] Initiating SyncJob {context.sync_id} "
            f"for ImportJob {context.import_job_id}"
        )

        # Retrieve the underlying import job to ensure it exists
        job_stmt = select(ImportJob).where(ImportJob.job_id == context.import_job_id)
        job_result = await session.execute(job_stmt)
        import_job = job_result.scalar_one_or_none()
        if not import_job:
            raise ValueError(f"ImportJob '{context.import_job_id}' does not exist.")

        # Save initial RUNNING SyncJob record in DB
        db_sync_job = SyncJob(
            sync_id=context.sync_id,
            import_job_id=context.import_job_id,
            started_at=result.started_at,
            status="RUNNING",
            correlation_id=context.correlation_id,
        )
        session.add(db_sync_job)
        await session.commit()

        # Execute nested transactional isolation savepoint
        nested_tx = await session.begin_nested()

        try:
            # 1. LOAD STAGING RECORDS
            details_stmt = select(StagingTicketDetail).where(
                StagingTicketDetail.job_id == context.import_job_id
            )
            details_res = await session.execute(details_stmt)
            staging_details = details_res.scalars().all()

            history_stmt = select(StagingTicketHistory).where(
                StagingTicketHistory.job_id == context.import_job_id
            )
            history_res = await session.execute(history_stmt)
            staging_history = history_res.scalars().all()

            time_stmt = select(StagingTimeEntry).where(
                StagingTimeEntry.job_id == context.import_job_id
            )
            time_res = await session.execute(time_stmt)
            staging_time = time_res.scalars().all()

            # 2. RESOLVE & SYNCHRONIZE TICKET DETAILS
            for detail in staging_details:
                # Resolve Master data using requested strategy rules
                client_name = detail.raw_data.get("client") if detail.raw_data else None
                engineer_name = (
                    detail.raw_data.get("engineer") if detail.raw_data else None
                )
                technology_name = (
                    detail.raw_data.get("technology") if detail.raw_data else None
                )

                team_id, team_warn = await resolver.resolve_team(
                    session, detail.assigned_team, context.team_resolver_strategy
                )
                client_id, client_warn = await resolver.resolve_client(
                    session, client_name, context.client_resolver_strategy
                )
                engineer_id, eng_warn = await resolver.resolve_engineer(
                    session, engineer_name, context.engineer_resolver_strategy
                )
                tech_id, tech_warn = await resolver.resolve_technology(
                    session, technology_name, context.technology_resolver_strategy
                )

                # Collect non-blocking warning diagnostics
                for warn in (team_warn, client_warn, eng_warn, tech_warn):
                    if warn:
                        result.warnings.append(
                            {"ticket_id": detail.ticket_id, "message": warn}
                        )

                # Handle Master Data Rejections
                is_rejected = (
                    (
                        context.team_resolver_strategy
                        == ResolverStrategy.REJECT_IF_MISSING
                        and team_warn
                    )
                    or (
                        context.client_resolver_strategy
                        == ResolverStrategy.REJECT_IF_MISSING
                        and client_warn
                    )
                    or (
                        context.engineer_resolver_strategy
                        == ResolverStrategy.REJECT_IF_MISSING
                        and eng_warn
                    )
                    or (
                        context.technology_resolver_strategy
                        == ResolverStrategy.REJECT_IF_MISSING
                        and tech_warn
                    )
                )

                if is_rejected:
                    result.rejected_records += 1
                    result.errors.append(
                        {
                            "ticket_id": detail.ticket_id,
                            "message": "Missing required Master Data reference.",
                        }
                    )
                    continue

                # Query if operational ticket exists
                ticket_stmt = select(Ticket).where(
                    Ticket.ticket_id_archer == detail.ticket_id
                )
                ticket_res = await session.execute(ticket_stmt)
                existing_ticket = ticket_res.scalar_one_or_none()

                incoming_vals = {
                    "ticket_id_archer": detail.ticket_id,
                    "title": detail.title,
                    "description": detail.description,
                    "created_date": detail.created_date,
                    "closed_date": detail.closed_date,
                    "status": detail.status,
                    "client_id": client_id,
                    "engineer_id": engineer_id,
                    "technology_id": tech_id,
                    "team_id": team_id,
                }

                if not existing_ticket:
                    # Apply INSERT
                    new_ticket = Ticket(
                        id=uuid.uuid4(),
                        **incoming_vals,
                    )
                    session.add(new_ticket)
                    result.inserted_records += 1
                else:
                    # Apply Change Detection comparing fields
                    has_changed, changes = self.change_detector.detect_changes(
                        existing_ticket, incoming_vals
                    )

                    if not has_changed:
                        result.unchanged_records += 1
                        continue

                    # Apply conflict strategy choices
                    if context.conflict_strategy == ConflictStrategy.IGNORE:
                        result.unchanged_records += 1
                        continue

                    if context.conflict_strategy == ConflictStrategy.DATABASE_WINS:
                        result.unchanged_records += 1
                        continue

                    # SOURCE_WINS or MOST_RECENT overwrite attributes
                    for attr, change in changes.items():
                        setattr(existing_ticket, attr, change["new"])
                    existing_ticket.updated_at = datetime.now(UTC).replace(tzinfo=None)
                    session.add(existing_ticket)
                    result.updated_records += 1

            # Flush ticket changes to guarantee referential keys are allocated
            await session.flush()

            # 3. SYNCHRONIZE TICKET HISTORY
            # Fetch set of valid operational ticket ID keys for checks
            valid_tickets_stmt = select(Ticket.ticket_id_archer)
            val_tkt_res = await session.execute(valid_tickets_stmt)
            operational_ticket_keys = set(val_tkt_res.scalars().all())

            # Query existing history IDs to prevent duplicate insertion
            exist_hist_stmt = select(TicketHistory.history_id_archer)
            exist_hist_res = await session.execute(exist_hist_stmt)
            existing_history_keys = set(exist_hist_res.scalars().all())

            for history in staging_history:
                # Validate Referential Integrity
                if history.ticket_id not in operational_ticket_keys:
                    result.rejected_records += 1
                    result.errors.append(
                        {
                            "history_id": history.history_id,
                            "message": f"Orphaned ticket: {history.ticket_id}",
                        }
                    )
                    continue

                # Idempotence: duplicate protection
                if history.history_id in existing_history_keys:
                    result.unchanged_records += 1
                    continue

                # Apply INSERT
                new_hist = TicketHistory(
                    id=uuid.uuid4(),
                    history_id_archer=history.history_id,
                    ticket_id=history.ticket_id,
                    change_date=history.change_date,
                    field_changed=history.field_changed,
                    old_value=history.old_value,
                    new_value=history.new_value,
                )
                session.add(new_hist)
                result.inserted_records += 1
                existing_history_keys.add(history.history_id)

            # 4. SYNCHRONIZE TIME ENTRIES
            # Query existing time entry IDs to prevent duplicates
            exist_time_stmt = select(TimeEntry.entry_id_archer)
            exist_time_res = await session.execute(exist_time_stmt)
            existing_time_keys = set(exist_time_res.scalars().all())

            for t_entry in staging_time:
                # Referential Integrity
                if t_entry.ticket_id not in operational_ticket_keys:
                    result.rejected_records += 1
                    result.errors.append(
                        {
                            "entry_id": t_entry.entry_id,
                            "message": f"Orphaned ticket: {t_entry.ticket_id}",
                        }
                    )
                    continue

                # Idempotence
                if t_entry.entry_id in existing_time_keys:
                    result.unchanged_records += 1
                    continue

                # Apply INSERT
                new_time = TimeEntry(
                    id=uuid.uuid4(),
                    entry_id_archer=t_entry.entry_id,
                    ticket_id=t_entry.ticket_id,
                    user_id=t_entry.user_id,
                    work_date=t_entry.work_date,
                    hours_spent=t_entry.hours_spent,
                    activity_type=t_entry.activity_type,
                )
                session.add(new_time)
                result.inserted_records += 1
                existing_time_keys.add(t_entry.entry_id)

            # 5. STEP 10: MARK SYNCHRONIZED STAGING ROWS
            now_sync = datetime.now(UTC).replace(tzinfo=None)
            for detail in staging_details:
                detail.synchronized_at = now_sync
                session.add(detail)

            for history in staging_history:
                # Mark history row as synchronized if it wasn't rejected
                history.synchronized_at = now_sync
                session.add(history)

            for t_entry in staging_time:
                t_entry.synchronized_at = now_sync
                session.add(t_entry)

            # Commit nested operational changes savepoint
            await nested_tx.commit()

            # Finalize Sync Job record
            await self._finalize_sync(
                session, db_sync_job, result, "COMPLETED", start_time_ns
            )
            logger.info(
                f"[{context.correlation_id}] Synchronization COMPLETED "
                f"for SyncJob {context.sync_id}"
            )
            return result

        except Exception as e:
            # Fatal Rollback of Nested Operational Changes only
            await nested_tx.rollback()
            error_msg = str(e)
            result.status = "FAILED"
            result.errors.append({"fatal_error": error_msg})

            logger.error(
                f"[{context.correlation_id}] Synchronization FAILED for "
                f"SyncJob {context.sync_id}: {error_msg}",
                exc_info=True,
            )
            # Commit the failed job stats tracking to maintain auditing history safely
            await self._finalize_sync(
                session, db_sync_job, result, "FAILED", start_time_ns
            )
            raise e

    async def _finalize_sync(
        self,
        session: AsyncSession,
        db_job: SyncJob,
        result: SynchronizationResult,
        status: str,
        start_time_ns: int,
    ) -> None:
        """Saves execution counts and finalized durations in DB."""
        duration_ms = (time.perf_counter_ns() - start_time_ns) // 1_000_000
        result.finished_at = datetime.now(UTC).replace(tzinfo=None)
        result.duration_ms = duration_ms
        result.status = status

        db_job.finished_at = result.finished_at
        db_job.duration_ms = duration_ms
        db_job.inserted_records = result.inserted_records
        db_job.updated_records = result.updated_records
        db_job.unchanged_records = result.unchanged_records
        db_job.rejected_records = result.rejected_records
        db_job.warnings = result.warnings
        db_job.errors = result.errors
        db_job.status = status

        session.add(db_job)
        await session.commit()
