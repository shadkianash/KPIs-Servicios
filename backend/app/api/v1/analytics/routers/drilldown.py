from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analytics.pagination.paginator import Paginator
from app.api.v1.analytics.schemas.envelope import ResponseEnvelope
from app.dependencies.db import get_db_session
from app.models.analytics import DailySnapshot, MonthlySnapshot

router = APIRouter()


async def _get_drilldown_snapshots(
    db: AsyncSession,
    field_name: str,
    entity_id: str,
    snapshot_type: str,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], Any]:
    """Helper query resolver for drill-down historical snapshot data."""
    if snapshot_type.lower() == "daily":
        daily_stmt = (
            select(DailySnapshot)
            .where(
                getattr(DailySnapshot, field_name) == entity_id,
                DailySnapshot.aggregation_level == field_name.replace("_id", ""),
            )
            .order_by(DailySnapshot.snapshot_date.desc())
        )
        records, info = await Paginator.paginate(db, daily_stmt, page, page_size)
        data = [
            {
                "snapshot_id": str(r.id),
                "snapshot_date": (
                    r.snapshot_date.isoformat().split("T")[0]
                    if r.snapshot_date
                    else None
                ),
                "aggregation_level": r.aggregation_level,
                "metrics": r.metrics,
                "snapshot_version": r.snapshot_version,
                "execution_id": str(r.execution_id),
            }
            for r in records
        ]
        return data, info
    elif snapshot_type.lower() == "monthly":
        monthly_stmt = (
            select(MonthlySnapshot)
            .where(
                getattr(MonthlySnapshot, field_name) == entity_id,
                MonthlySnapshot.aggregation_level == field_name.replace("_id", ""),
            )
            .order_by(MonthlySnapshot.year.desc(), MonthlySnapshot.month.desc())
        )
        records, info = await Paginator.paginate(db, monthly_stmt, page, page_size)
        data = [
            {
                "snapshot_id": str(r.id),
                "year": r.year,
                "month": r.month,
                "aggregation_level": r.aggregation_level,
                "metrics": r.metrics,
                "snapshot_version": r.snapshot_version,
                "execution_id": str(r.execution_id),
            }
            for r in records
        ]
        return data, info
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'type' must be either 'daily' or 'monthly'.",
        )


@router.get(
    "/drilldown/engineer/{engineer_id}",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Engineer analytical drill-down",
)
async def get_engineer_drilldown(
    engineer_id: str,
    type: str = Query("monthly", description="Snapshot type ('daily' or 'monthly')."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes historical KPI snapshot evolution for an Engineer."""
    data, info = await _get_drilldown_snapshots(
        db, "engineer_id", engineer_id, type, page, page_size
    )
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/drilldown/client/{client_id}",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Client analytical drill-down",
)
async def get_client_drilldown(
    client_id: str,
    type: str = Query("monthly", description="Snapshot type ('daily' or 'monthly')."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes historical KPI snapshot evolution for a Client."""
    data, info = await _get_drilldown_snapshots(
        db, "client_id", client_id, type, page, page_size
    )
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/drilldown/technology/{technology_id}",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Technology analytical drill-down",
)
async def get_technology_drilldown(
    technology_id: str,
    type: str = Query("monthly", description="Snapshot type ('daily' or 'monthly')."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes historical KPI snapshot evolution for a Technology."""
    data, info = await _get_drilldown_snapshots(
        db, "technology_id", technology_id, type, page, page_size
    )
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/drilldown/team/{team_id}",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Team analytical drill-down",
)
async def get_team_drilldown(
    team_id: str,
    type: str = Query("monthly", description="Snapshot type ('daily' or 'monthly')."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes historical KPI snapshot evolution for a Team."""
    data, info = await _get_drilldown_snapshots(
        db, "team_id", team_id, type, page, page_size
    )
    return ResponseEnvelope(success=True, data=data, pagination=info)
