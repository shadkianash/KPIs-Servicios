import math
from collections.abc import Sequence
from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analytics.schemas.envelope import PaginationInfo

T = TypeVar("T")


class Paginator:
    """Utility helper to paginate asynchronous SQLAlchemy queries cleanly."""

    @staticmethod
    async def paginate(
        session: AsyncSession,
        query: Any,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[Any], PaginationInfo]:
        """Executes pagination count and offset fetches on any base SQLAlchemy query."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50

        # 1. Calculate total record count
        # Strip order_by to optimize counting speed if needed
        count_stmt = select(func.count()).select_from(query.subquery())
        count_res = await session.execute(count_stmt)
        total_records = count_res.scalar_one()

        # 2. Derive page metrics
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 0

        if page > total_pages and total_pages > 0:
            page = total_pages

        offset = (page - 1) * page_size

        # 3. Fetch matched records
        paged_stmt = query.offset(offset).limit(page_size)
        records_res = await session.execute(paged_stmt)
        records = records_res.scalars().all()

        info = PaginationInfo(
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
        )

        return records, info
