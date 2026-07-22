import polars as pl

from app.etl.core.models import SchemaError
from app.etl.schemas.base import BaseSchema


class SchemaValidator:
    """Verifies that the ingested DataFrame structure matches schemas."""

    def validate(self, df: pl.DataFrame, schema: BaseSchema) -> None:
        """Asserts that all required columns are present in the DataFrame."""
        if df.is_empty():
            raise SchemaError("The ingested CSV is empty and cannot be processed.")

        missing_columns = []
        for req_col in schema.required_columns:
            if req_col not in df.columns:
                missing_columns.append(req_col)

        if missing_columns:
            raise SchemaError(
                f"Missing required columns in source file: {missing_columns}"
            )
