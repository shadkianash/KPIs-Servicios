from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analytics.filters.query_parser import QueryParser
from app.api.v1.analytics.pagination.paginator import Paginator
from app.api.v1.analytics.schemas.envelope import ResponseEnvelope
from app.dependencies.db import get_db_session
from app.models.analytics import DailySnapshot, MonthlySnapshot

router = APIRouter()


@router.get(
    "/kpi/daily",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Retrieve Daily KPI Snapshots",
)
async def get_daily_snapshots(
    start_date: date | None = Query(None, description="Filter start date."),
    end_date: date | None = Query(None, description="Filter end date."),
    engineer_id: str | None = Query(None),
    client_id: str | None = Query(None),
    technology_id: str | None = Query(None),
    team_id: str | None = Query(None),
    sort: str | None = Query(None, description="Generic sorting lookup key."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Retrieves computed daily KPI snapshots with full filtering and sorting."""
    stmt = select(DailySnapshot)

    # Composable Filters
    if start_date:
        stmt = stmt.where(DailySnapshot.snapshot_date >= start_date)
    if end_date:
        stmt = stmt.where(DailySnapshot.snapshot_date <= end_date)

    filters = {
        "engineer_id": engineer_id,
        "client_id": client_id,
        "technology_id": technology_id,
        "team_id": team_id,
    }
    stmt = QueryParser.apply_filters(stmt, DailySnapshot, filters)

    # Generic Sorting
    allowed_sorting_cols = {
        "snapshot_date",
        "aggregation_level",
        "engineer_id",
        "client_id",
        "technology_id",
        "team_id",
    }
    stmt = QueryParser.apply_sorting(stmt, DailySnapshot, sort, allowed_sorting_cols)

    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [
        {
            "id": str(r.id),
            "snapshot_date": (
                r.snapshot_date.isoformat().split("T")[0] if r.snapshot_date else None
            ),
            "aggregation_level": r.aggregation_level,
            "engineer_id": r.engineer_id,
            "client_id": r.client_id,
            "technology_id": r.technology_id,
            "team_id": r.team_id,
            "snapshot_version": r.snapshot_version,
            "execution_id": str(r.execution_id),
            "metrics": r.metrics,
        }
        for r in records
    ]
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/kpi/monthly",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Retrieve Monthly KPI Snapshots",
)
async def get_monthly_snapshots(
    year: int | None = Query(None, ge=1900),
    month: int | None = Query(None, ge=1, le=12),
    engineer_id: str | None = Query(None),
    client_id: str | None = Query(None),
    technology_id: str | None = Query(None),
    team_id: str | None = Query(None),
    sort: str | None = Query(None, description="Generic sorting lookup key."),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Retrieves computed monthly KPI snapshots with full filtering and sorting."""
    stmt = select(MonthlySnapshot)

    filters = {
        "year": year,
        "month": month,
        "engineer_id": engineer_id,
        "client_id": client_id,
        "technology_id": technology_id,
        "team_id": team_id,
    }
    stmt = QueryParser.apply_filters(stmt, MonthlySnapshot, filters)

    # Generic Sorting
    allowed_sorting_cols = {
        "year",
        "month",
        "aggregation_level",
        "engineer_id",
        "client_id",
        "technology_id",
        "team_id",
    }
    stmt = QueryParser.apply_sorting(stmt, MonthlySnapshot, sort, allowed_sorting_cols)

    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [
        {
            "id": str(r.id),
            "year": r.year,
            "month": r.month,
            "aggregation_level": r.aggregation_level,
            "engineer_id": r.engineer_id,
            "client_id": r.client_id,
            "technology_id": r.technology_id,
            "team_id": r.team_id,
            "snapshot_version": r.snapshot_version,
            "execution_id": str(r.execution_id),
            "metrics": r.metrics,
        }
        for r in records
    ]
    return ResponseEnvelope(success=True, data=data, pagination=info)
