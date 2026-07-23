import logging
from typing import Any

import sqlalchemy as sa

logger = logging.getLogger(__name__)


class QueryParser:
    """Parses composable filters and generic JSONB sorting keys for SQLAlchemy."""

    @staticmethod
    def apply_sorting(
        query: Any,
        model: Any,
        sort_param: str | None,
        allowed_columns: set[str],
    ) -> Any:
        """Parses sort param and applies sorting (supports metrics.key)."""
        if not sort_param:
            # Default sorting to date/chronological field if present
            if hasattr(model, "snapshot_date"):
                return query.order_by(model.snapshot_date.desc())
            if hasattr(model, "year"):
                return query.order_by(model.year.desc(), model.month.desc())
            return query

        descending = sort_param.startswith("-")
        clean_param = sort_param.lstrip("-").strip()

        # Check if it is a JSONB path lookup (e.g. 'metrics.tickets_closed')
        if clean_param.startswith("metrics."):
            metric_key = clean_param.split(".", 1)[1]
            # Extract and cast JSONB element to float to ensure correct numeric sorting
            # (prevents "10" from sorting before "2" alphabetically!)
            json_expr = sa.func.jsonb_extract_path_text(model.metrics, metric_key)
            # Safe float cast
            cast_expr = sa.cast(json_expr, sa.Float)

            sort_expr = cast_expr.desc() if descending else cast_expr.asc()
            return query.order_by(sort_expr)

        # Standard column lookup
        if clean_param in allowed_columns and hasattr(model, clean_param):
            col_expr = getattr(model, clean_param)
            sort_expr = col_expr.desc() if descending else col_expr.asc()
            return query.order_by(sort_expr)

        # Log invalid sort parameters and return original query unmodified
        logger.warning(f"Ignored invalid sort parameter: {sort_param}")
        return query

    @staticmethod
    def apply_filters(
        query: Any,
        model: Any,
        filters: dict[str, Any],
    ) -> Any:
        """Applies a composable dictionary of column filters to the base query."""
        for field, val in filters.items():
            if val is None:
                continue

            if hasattr(model, field):
                col = getattr(model, field)
                query = query.where(col == val)

        return query
