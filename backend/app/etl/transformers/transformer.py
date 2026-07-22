import datetime as dt
from typing import Any

import polars as pl

from app.etl.schemas.base import BaseSchema


class Transformer:
    """Standardizes, casts, and fills default values on a validated Polars DataFrame."""

    def transform(self, df: pl.DataFrame, schema: BaseSchema) -> list[dict[str, Any]]:
        """Applies type transformations, fills defaults, and outputs list of records."""
        if df.is_empty():
            return []

        # 1. Fill default values for missing columns / Null optional values
        filled_df = df
        for col in schema.columns:
            # If the column is completely missing from the CSV, create it with Nulls
            if col.name not in filled_df.columns:
                filled_df = filled_df.with_columns(pl.lit(None).alias(col.name))

            # Apply default values where null
            if col.default_value is not None:
                filled_df = filled_df.with_columns(
                    pl.col(col.name).fill_null(col.default_value).alias(col.name)
                )

        # 2. Iterate and cast records to native Python/SQL types
        transformed_records = []
        for row in filled_df.iter_rows(named=True):
            record: dict[str, Any] = {}
            for col in schema.columns:
                val = row.get(col.name)
                if val is None:
                    record[col.name] = None
                    continue

                # Parse and cast according to column spec
                if col.target_type == "datetime":
                    record[col.name] = self._parse_datetime(str(val))
                elif col.target_type in ("int", "integer"):
                    record[col.name] = int(val)
                elif col.target_type in ("float", "numeric"):
                    record[col.name] = float(val)
                elif col.target_type == "bool":
                    record[col.name] = str(val).lower() in ("true", "1", "yes", "on")
                else:
                    record[col.name] = str(val)

            # Store raw unmodified JSON data alongside for auditing/future extensibility
            # Extract only columns that are part of the original df (excluding indexes)
            raw_audit = {
                k: row[k] for k in df.columns if k in row and row[k] is not None
            }
            record["raw_data"] = raw_audit

            transformed_records.append(record)

        return transformed_records

    def _parse_datetime(self, val: str) -> dt.datetime:
        """Helper to parse a date string using common formats."""
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y",
        ):
            try:
                return dt.datetime.strptime(val, fmt)
            except ValueError:
                continue
        # Fallback to standard isoformat parse
        return dt.datetime.fromisoformat(val)
