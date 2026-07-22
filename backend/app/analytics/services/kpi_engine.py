import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import polars as pl
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.core.registry import calculator_registry
from app.analytics.core.registry_bootstrap import bootstrap_registry
from app.models.analytics import DailySnapshot, KPIExecution, MonthlySnapshot
from app.models.operational import Ticket, TicketHistory, TimeEntry

logger = logging.getLogger(__name__)


class KPIEngine:
    """Core vectorized KPI calculations and snapshots orchestrator."""

    def __init__(self) -> None:
        bootstrap_registry()

    async def calculate_and_snapshot(
        self, session: AsyncSession, correlation_id: str | None = None
    ) -> uuid.UUID:
        """Executes the complete KPI snapshot pipeline."""
        start_time_ns = time.perf_counter_ns()
        exec_id = uuid.uuid4()
        corr_id = correlation_id or f"kpi-{uuid.uuid4()}"

        logger.info(f"[{corr_id}] Starting KPI calculation run: {exec_id}")

        # Create running KPIExecution audit tracking
        db_exec = KPIExecution(
            execution_id=exec_id,
            execution_status="RUNNING",
            correlation_id=corr_id,
        )
        session.add(db_exec)
        await session.commit()

        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        try:
            # 1. LOAD SYNCHRONIZED OPERATIONAL DATA
            tkt_res = await session.execute(select(Ticket))
            tickets = tkt_res.scalars().all()

            hist_res = await session.execute(select(TicketHistory))
            history = hist_res.scalars().all()

            time_res = await session.execute(select(TimeEntry))
            time_entries = time_res.scalars().all()

            # Record metrics
            db_exec.processed_tickets = len(tickets)
            db_exec.processed_time_entries = len(time_entries)

            # Convert database entities to pure Python dicts for Polars DataFrames
            tickets_data = [
                {
                    "id": str(t.id),
                    "ticket_id_archer": t.ticket_id_archer,
                    "title": t.title,
                    "description": t.description,
                    "created_date": t.created_date,
                    "closed_date": t.closed_date,
                    "status": t.status,
                    "client_id": str(t.client_id) if t.client_id else None,
                    "engineer_id": str(t.engineer_id) if t.engineer_id else None,
                    "technology_id": str(t.technology_id) if t.technology_id else None,
                    "team_id": str(t.team_id) if t.team_id else None,
                }
                for t in tickets
            ]

            hist_data = [
                {
                    "id": str(h.id),
                    "history_id_archer": h.history_id_archer,
                    "ticket_id": h.ticket_id,
                    "change_date": h.change_date,
                    "field_changed": h.field_changed,
                    "old_value": h.old_value,
                    "new_value": h.new_value,
                }
                for h in history
            ]

            time_data = [
                {
                    "id": str(te.id),
                    "entry_id_archer": te.entry_id_archer,
                    "ticket_id": te.ticket_id,
                    "user_id": te.user_id,
                    "work_date": te.work_date,
                    "hours_spent": te.hours_spent,
                    "activity_type": te.activity_type,
                }
                for te in time_entries
            ]

            # Ingest into Polars DataFrames
            tickets_df = pl.DataFrame(tickets_data)
            history_df = pl.DataFrame(hist_data)
            time_df = pl.DataFrame(time_data)

            # Add timestamp fields safely to DataFrames if empty
            if tickets_df.is_empty():
                tickets_df = pl.DataFrame(
                    schema={
                        "id": pl.String,
                        "ticket_id_archer": pl.String,
                        "title": pl.String,
                        "created_date": pl.Datetime,
                        "closed_date": pl.Datetime,
                        "status": pl.String,
                        "client_id": pl.String,
                        "engineer_id": pl.String,
                        "technology_id": pl.String,
                        "team_id": pl.String,
                    }
                )
            if history_df.is_empty():
                history_df = pl.DataFrame(
                    schema={
                        "id": pl.String,
                        "ticket_id": pl.String,
                        "change_date": pl.Datetime,
                        "field_changed": pl.String,
                    }
                )
            if time_df.is_empty():
                time_df = pl.DataFrame(
                    schema={
                        "id": pl.String,
                        "ticket_id": pl.String,
                        "work_date": pl.Datetime,
                        "hours_spent": pl.Float64,
                    }
                )

            # Extract date & month helper analytical keys for time windows
            if not tickets_df.is_empty():
                tickets_df = tickets_df.with_columns(
                    # Derive snapshot date key representing Year-Month-Day naive
                    pl.col("created_date").dt.truncate("1d").alias("snapshot_date"),
                    pl.col("created_date").dt.year().alias("year"),
                    pl.col("created_date").dt.month().alias("month"),
                )

            if not time_df.is_empty() and "work_date" in time_df.columns:
                time_df = time_df.with_columns(
                    pl.col("work_date").dt.truncate("1d").alias("snapshot_date"),
                    pl.col("work_date").dt.year().alias("year"),
                    pl.col("work_date").dt.month().alias("month"),
                )

            # Join time_df with parent ticket dimensions
            if not time_df.is_empty() and not tickets_df.is_empty():
                ticket_dimensions = tickets_df.select(
                    [
                        "ticket_id_archer",
                        "client_id",
                        "engineer_id",
                        "technology_id",
                        "team_id",
                    ]
                )
                time_df = time_df.join(
                    ticket_dimensions,
                    left_on="ticket_id",
                    right_on="ticket_id_archer",
                    how="left",
                )
            elif not time_df.is_empty():
                # Inject missing dimension columns if tickets_df is empty
                time_df = time_df.with_columns(
                    pl.lit(None).alias("client_id"),
                    pl.lit(None).alias("engineer_id"),
                    pl.lit(None).alias("technology_id"),
                    pl.lit(None).alias("team_id"),
                )

            # 2. RUN DATA QUALITY VALIDATIONS
            # Check for negative durations
            if not tickets_df.is_empty() and "closed_date" in tickets_df.columns:
                neg_res = tickets_df.filter(
                    pl.col("closed_date") < pl.col("created_date")
                )
                for row in neg_res.iter_rows(named=True):
                    warnings.append(
                        {
                            "ticket_id": row["ticket_id_archer"],
                            "type": "negative_resolution_time",
                            "message": "closed_date is prior to created_date.",
                        }
                    )

            datasets = {
                "tickets": tickets_df,
                "history": history_df,
                "time_entries": time_df,
            }

            # Configured aggregation mappings
            agg_mappings = {
                "engineer": ["engineer_id"],
                "client": ["client_id"],
                "technology": ["technology_id"],
                "team": ["team_id"],
                "day": ["snapshot_date"],
                "month": ["year", "month"],
                "global": [],
            }

            daily_count = 0
            monthly_count = 0

            # 3. EXECUTE CALCULATION ENGINE LOOPS PER AGGREGATION LEVEL
            for level, group_cols in agg_mappings.items():
                logger.info(
                    f"[{corr_id}] Calculating KPIs for aggregation level: {level}"
                )

                level_df = None

                for calculator in calculator_registry.get_calculators():
                    if level not in calculator.supported_aggregation_levels:
                        continue

                    # Execute Calculator
                    calc_res = calculator.calculate(datasets, group_cols)
                    if calc_res.is_empty():
                        continue

                    if level_df is None:
                        level_df = calc_res
                    else:
                        if not group_cols:
                            # Global level merges single-row metrics horizontally
                            level_df = pl.concat(
                                [level_df, calc_res], how="horizontal_extend"
                            )
                        else:
                            level_df = level_df.join(
                                calc_res, on=group_cols, how="full", coalesce=True
                            )

                if level_df is None or level_df.is_empty():
                    continue

                # 4. BATCH PERSIST GENERATED SNAPSHOTS
                if level == "day":
                    # Delete existing daily snapshots for safety & idempotency
                    await session.execute(delete(DailySnapshot))

                    for row in level_df.iter_rows(named=True):
                        # Construct metrics map
                        metrics = {
                            k: v
                            for k, v in row.items()
                            if k not in group_cols and v is not None
                        }

                        snap_date = row.get("snapshot_date")
                        if not snap_date:
                            continue

                        new_daily = DailySnapshot(
                            id=uuid.uuid4(),
                            snapshot_date=snap_date,
                            aggregation_level=level,
                            execution_id=exec_id,
                            metrics=metrics,
                        )
                        session.add(new_daily)
                        daily_count += 1
                else:
                    # Non-day aggregations saved in MonthlySnapshot (within transaction)
                    await session.execute(
                        delete(MonthlySnapshot).where(
                            MonthlySnapshot.aggregation_level == level
                        )
                    )

                    for row in level_df.iter_rows(named=True):
                        metrics = {
                            k: v
                            for k, v in row.items()
                            if k not in group_cols and v is not None
                        }

                        # Derive year/month parameters
                        snap_year = row.get("year", datetime.now(UTC).year)
                        snap_month = row.get("month", datetime.now(UTC).month)

                        new_monthly = MonthlySnapshot(
                            id=uuid.uuid4(),
                            year=int(snap_year),
                            month=int(snap_month),
                            aggregation_level=level,
                            engineer_id=(
                                str(row.get("engineer_id"))
                                if row.get("engineer_id")
                                else None
                            ),
                            client_id=(
                                str(row.get("client_id"))
                                if row.get("client_id")
                                else None
                            ),
                            technology_id=(
                                str(row.get("technology_id"))
                                if row.get("technology_id")
                                else None
                            ),
                            team_id=(
                                str(row.get("team_id")) if row.get("team_id") else None
                            ),
                            execution_id=exec_id,
                            metrics=metrics,
                        )
                        session.add(new_monthly)
                        monthly_count += 1

            # Commit additions safely at the end of all level loops atomicity
            await session.commit()

            # 5. FINALIZE SUCCESSFUL CALCULATION METRICS
            db_exec.generated_daily_snapshots = daily_count
            db_exec.generated_monthly_snapshots = monthly_count
            await self._finalize_exec(
                session, db_exec, "COMPLETED", start_time_ns, warnings, errors
            )
            logger.info(
                f"[{corr_id}] KPI engine calculation finished successfully. "
                f"Daily: {daily_count}, Monthly: {monthly_count}"
            )
            return exec_id

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{corr_id}] KPI engine failure: {error_msg}", exc_info=True)
            errors.append({"fatal_error": error_msg})

            # Rollback uncommitted snapshots, but commit FAILED execution metadata
            await session.rollback()
            await self._finalize_exec(
                session, db_exec, "FAILED", start_time_ns, warnings, errors
            )
            raise e

    async def _finalize_exec(
        self,
        session: AsyncSession,
        db_exec: KPIExecution,
        status: str,
        start_time_ns: int,
        warnings: list[dict[str, Any]],
        errors: list[dict[str, Any]],
    ) -> None:
        """Persists tracking statistics and runtime run details in DB."""
        duration_ms = (time.perf_counter_ns() - start_time_ns) // 1_000_000
        db_exec.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db_exec.duration_ms = duration_ms
        db_exec.execution_status = status
        db_exec.warnings = warnings
        db_exec.errors = errors

        session.add(db_exec)
        await session.commit()
