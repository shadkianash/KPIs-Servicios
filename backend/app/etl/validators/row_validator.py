import datetime as dt
import re

import polars as pl

from app.etl.core.models import ValidationFailure
from app.etl.schemas.base import BaseSchema


class RowValidator:
    """Validates data types, constraints, formats, and duplicates on rows."""

    UUID_REGEX = re.compile(
        r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
    )

    def validate_rows(
        self, df: pl.DataFrame, schema: BaseSchema
    ) -> tuple[pl.DataFrame, list[ValidationFailure]]:
        """Checks row-level validation rules.

        Isolates failures and returns a cleaned/valid DataFrame alongside failures.
        """
        failures: list[ValidationFailure] = []
        if df.is_empty():
            return df, failures

        # To track rows to exclude, keep set of invalid row indices.
        # Polars has 0-based index. Let's add a temporary `__row_idx__` column.
        df_with_idx = df.with_row_index("__row_idx__")
        invalid_row_indices: set[int] = set()

        # 1. Non-null validation on required columns
        for col in schema.columns:
            if col.name not in df_with_idx.columns:
                if col.required:
                    # Missing required column completely
                    failures.append(
                        ValidationFailure(
                            row_index=1,
                            field_name=col.name,
                            error_type="missing_field",
                            message=f"Required column '{col.name}' is missing.",
                            raw_value=None,
                        )
                    )
                continue

            if col.required:
                null_rows = df_with_idx.filter(pl.col(col.name).is_null())
                for row in null_rows.iter_rows(named=True):
                    idx = int(row["__row_idx__"])
                    invalid_row_indices.add(idx)
                    failures.append(
                        ValidationFailure(
                            row_index=idx + 1,  # 1-based index
                            field_name=col.name,
                            error_type="missing_field",
                            message=f"Required column '{col.name}' cannot be null.",
                            raw_value=None,
                        )
                    )

        # 2. Type validation
        for col in schema.columns:
            if col.name not in df_with_idx.columns:
                continue

            non_null_rows = df_with_idx.filter(
                pl.col(col.name).is_not_null()
                & (~pl.col("__row_idx__").is_in(list(invalid_row_indices)))
            )

            if col.target_type == "uuid":
                for row in non_null_rows.iter_rows(named=True):
                    val = str(row[col.name])
                    if not self.UUID_REGEX.match(val):
                        idx = int(row["__row_idx__"])
                        invalid_row_indices.add(idx)
                        failures.append(
                            ValidationFailure(
                                row_index=idx + 1,
                                field_name=col.name,
                                error_type="type_mismatch",
                                message=f"Column '{col.name}' must be a valid UUID.",
                                raw_value=val,
                            )
                        )

            elif col.target_type in ("int", "integer"):
                for row in non_null_rows.iter_rows(named=True):
                    val = str(row[col.name])
                    try:
                        int(val)
                    except ValueError:
                        idx = int(row["__row_idx__"])
                        invalid_row_indices.add(idx)
                        failures.append(
                            ValidationFailure(
                                row_index=idx + 1,
                                field_name=col.name,
                                error_type="type_mismatch",
                                message=f"Column '{col.name}' must be a valid integer.",
                                raw_value=val,
                            )
                        )

            elif col.target_type in ("float", "numeric"):
                for row in non_null_rows.iter_rows(named=True):
                    val = str(row[col.name])
                    try:
                        float(val)
                    except ValueError:
                        idx = int(row["__row_idx__"])
                        invalid_row_indices.add(idx)
                        failures.append(
                            ValidationFailure(
                                row_index=idx + 1,
                                field_name=col.name,
                                error_type="type_mismatch",
                                message=f"Column '{col.name}' must be a valid float.",
                                raw_value=val,
                            )
                        )

            elif col.target_type == "datetime":
                for row in non_null_rows.iter_rows(named=True):
                    val = str(row[col.name])
                    parsed = False
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
                            dt.datetime.strptime(val, fmt)
                            parsed = True
                            break
                        except ValueError:
                            continue

                    if not parsed:
                        idx = int(row["__row_idx__"])
                        invalid_row_indices.add(idx)
                        failures.append(
                            ValidationFailure(
                                row_index=idx + 1,
                                field_name=col.name,
                                error_type="type_mismatch",
                                message=f"Column '{col.name}' must be a valid date.",
                                raw_value=val,
                            )
                        )

        # 3. Duplicate Business Key detection inside the file itself
        pk_col = schema.primary_key
        if pk_col in df_with_idx.columns:
            non_invalid_rows = df_with_idx.filter(
                ~pl.col("__row_idx__").is_in(list(invalid_row_indices))
            )
            pks = non_invalid_rows.select([pl.col(pk_col), pl.col("__row_idx__")])
            duplicates = (
                pks.group_by(pk_col)
                .agg(pl.len().alias("count"), pl.col("__row_idx__").alias("indices"))
                .filter(pl.col("count") > 1)
            )

            for dup_row in duplicates.iter_rows(named=True):
                val = str(dup_row[pk_col])
                indices = list(dup_row["indices"])
                # Flag subsequent rows as duplicated (the first is considered valid)
                for idx in indices[1:]:
                    invalid_row_indices.add(idx)
                    failures.append(
                        ValidationFailure(
                            row_index=idx + 1,
                            field_name=pk_col,
                            error_type="duplicate_key",
                            message=f"Duplicate key '{val}' within the import file.",
                            raw_value=val,
                        )
                    )

        valid_df = df_with_idx.filter(
            ~pl.col("__row_idx__").is_in(list(invalid_row_indices))
        ).drop("__row_idx__")

        return valid_df, failures
