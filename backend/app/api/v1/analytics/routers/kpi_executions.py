import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analytics.pagination.paginator import Paginator
from app.api.v1.analytics.schemas.envelope import ResponseEnvelope
from app.dependencies.db import get_db_session
from app.models.analytics import KPIExecution

router = APIRouter()


@router.get(
    "/kpi/executions",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="List KPI calculation runs",
)
async def get_kpi_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes all KPI execution run history records with pagination."""
    stmt = select(KPIExecution).order_by(KPIExecution.started_at.desc())
    records, info = await Paginator.paginate(db, stmt, page, page_size)

    data = [
        {
            "execution_id": str(r.execution_id),
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "duration_ms": r.duration_ms,
            "execution_status": r.execution_status,
            "calculation_version": r.calculation_version,
            "engine_version": r.engine_version,
            "processed_tickets": r.processed_tickets,
            "processed_time_entries": r.processed_time_entries,
            "generated_daily_snapshots": r.generated_daily_snapshots,
            "generated_monthly_snapshots": r.generated_monthly_snapshots,
            "correlation_id": r.correlation_id,
        }
        for r in records
    ]
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/kpi/executions/{execution_id}",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Retrieve single KPI run metadata",
)
async def get_kpi_execution_detail(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[dict[str, Any]]:
    """Retrieve detailed run stats, errors of a KPIExecution."""
    stmt = select(KPIExecution).where(KPIExecution.execution_id == execution_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"KPI Execution '{execution_id}' not found.",
        )

    data = {
        "execution_id": str(record.execution_id),
        "started_at": record.started_at.isoformat() if record.started_at else None,
        "finished_at": record.finished_at.isoformat() if record.finished_at else None,
        "duration_ms": record.duration_ms,
        "execution_status": record.execution_status,
        "calculation_version": record.calculation_version,
        "engine_version": record.engine_version,
        "processed_tickets": record.processed_tickets,
        "processed_time_entries": record.processed_time_entries,
        "generated_daily_snapshots": record.generated_daily_snapshots,
        "generated_monthly_snapshots": record.generated_monthly_snapshots,
        "warnings": record.warnings,
        "errors": record.errors,
        "correlation_id": record.correlation_id,
        "source_import_job_ids": record.source_import_job_ids,
        "execution_parameters": record.execution_parameters,
    }
    return ResponseEnvelope(success=True, data=data)
