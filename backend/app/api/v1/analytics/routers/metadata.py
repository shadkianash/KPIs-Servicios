from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analytics.pagination.paginator import Paginator
from app.api.v1.analytics.schemas.envelope import ResponseEnvelope
from app.dependencies.db import get_db_session
from app.models.operational import Client, Engineer, Team, Technology

router = APIRouter()


@router.get(
    "/metadata/clients",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Active clients catalog",
)
async def get_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes list of active Clients with pagination."""
    stmt = select(Client).where(Client.is_active).order_by(Client.name.asc())
    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [{"id": str(r.id), "name": r.name} for r in records]
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/metadata/technologies",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Active technologies catalog",
)
async def get_technologies(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes list of active Technologies with pagination."""
    stmt = (
        select(Technology).where(Technology.is_active).order_by(Technology.name.asc())
    )
    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [{"id": str(r.id), "name": r.name} for r in records]
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/metadata/engineers",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Active engineers catalog",
)
async def get_engineers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes list of active Engineers with pagination."""
    stmt = select(Engineer).where(Engineer.is_active).order_by(Engineer.name.asc())
    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [{"id": str(r.id), "name": r.name} for r in records]
    return ResponseEnvelope(success=True, data=data, pagination=info)


@router.get(
    "/metadata/teams",
    response_model=ResponseEnvelope[list[dict[str, Any]]],
    summary="Active teams catalog",
)
async def get_teams(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[list[dict[str, Any]]]:
    """Exposes list of active Teams with pagination."""
    stmt = select(Team).where(Team.is_active).order_by(Team.name.asc())
    records, info = await Paginator.paginate(db, stmt, page, page_size)
    data = [{"id": str(r.id), "name": r.name} for r in records]
    return ResponseEnvelope(success=True, data=data, pagination=info)
