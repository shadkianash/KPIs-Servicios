import io

import polars as pl

from app.etl.core.models import SchemaError
from app.etl.schemas.base import BaseSchema


class CSVReader:
    """Reads raw CSV bytes, trims whitespaces, and standardizes headers."""

    def read(
        self,
        content_bytes: bytes,
        schema: BaseSchema,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> pl.DataFrame:
        """Decodes raw bytes, maps aliases, and trims column data."""
        # 1. Decode bytes using requested encoding
        try:
            # Handle BOM and encoding gracefully
            decoded_text = content_bytes.decode(encoding)
        except UnicodeDecodeError as e:
            # Attempt cp1252 fallback or raise
            raise SchemaError(
                f"Failed to decode CSV content using encoding '{encoding}': {e}"
            ) from e

        # Remove UTF-8 BOM if present manually as a safeguard
        if decoded_text.startswith("\ufeff"):
            decoded_text = decoded_text[1:]

        # Return empty DataFrame immediately if the string is empty
        if not decoded_text.strip():
            return pl.DataFrame()

        # 2. Parse using Polars CSV reader
        try:
            df = pl.read_csv(
                io.BytesIO(decoded_text.encode("utf-8")),
                separator=delimiter,
                infer_schema=False,  # Treat fields as string for ETL casting
            )
        except Exception as e:
            raise SchemaError(f"Failed to parse CSV tabular format: {e}") from e

        if df.is_empty():
            return pl.DataFrame()

        # 3. Standardize headers based on aliases
        headers = [col.lower().strip() for col in df.columns]
        standardized_headers = []
        alias_map = schema.aliases

        for h in headers:
            if h in alias_map:
                standardized_headers.append(alias_map[h])
            else:
                standardized_headers.append(h)

        df.columns = standardized_headers

        # 4. Clean strings: Trim whitespace and normalize empty values to None
        for col_name in df.columns:
            clean_col = pl.col(col_name).str.strip_chars()
            df = df.with_columns(
                pl.when(
                    clean_col.is_null()
                    | (clean_col == "")
                    | (clean_col.str.strip_chars() == "")
                )
                .then(None)
                .otherwise(clean_col)
                .alias(col_name)
            )

        return df
