import polars as pl

from app.analytics.core.base_calculator import BaseCalculator


class FirstResponseTimeCalculator(BaseCalculator):
    """Calculates the average first response time in hours."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        return "average_response_time"

    @property
    def description(self) -> str:
        return "Average elapsed hours from ticket creation to first status change."

    @property
    def required_datasets(self) -> list[str]:
        return ["tickets", "history"]

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        tickets_df = datasets["tickets"]
        history_df = datasets["history"]

        if tickets_df.is_empty() or history_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # 1. Isolate the first status transition for each ticket
        status_changes = history_df.filter(pl.col("field_changed") == "status")
        if status_changes.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # Sort and group by ticket_id to find the earliest change_date
        first_changes = (
            status_changes.sort("change_date")
            .group_by("ticket_id")
            .agg(pl.col("change_date").first().alias("first_change_date"))
        )

        # 2. Join Earliest Status Change with Tickets
        joined = tickets_df.join(
            first_changes,
            left_on="ticket_id_archer",
            right_on="ticket_id",
            how="inner",
        )

        # Calculate duration in hours
        duration_df = joined.with_columns(
            (
                (
                    pl.col("first_change_date") - pl.col("created_date")
                ).dt.total_milliseconds()
                / (3600 * 1000)
            ).alias("response_hours")
        ).filter(pl.col("response_hours") >= 0)  # Filter anomalies (dates out of order)

        if duration_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # 3. Group and compute the average duration
        return duration_df.group_by(group_cols).agg(
            pl.col("response_hours").mean().fill_null(0.0).alias(self.name)
        )


class ResolutionTimeCalculator(BaseCalculator):
    """Calculates the average ticket resolution time in elapsed hours."""

    def __init__(self, terminal_statuses: list[str] | None = None) -> None:
        self.terminal_statuses = terminal_statuses or ["Closed", "Resolved"]

    @property
    def name(self) -> str:
        return "average_resolution_time"

    @property
    def description(self) -> str:
        return "Average elapsed hours from ticket creation to terminal close state."

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        tickets_df = datasets["tickets"]
        if tickets_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # Filter only terminal resolved tickets
        resolved_df = tickets_df.filter(
            pl.col("status").is_in(self.terminal_statuses)
            & pl.col("closed_date").is_not_null()
        )

        if resolved_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # Calculate resolution duration in hours
        duration_df = resolved_df.with_columns(
            (
                (pl.col("closed_date") - pl.col("created_date")).dt.total_milliseconds()
                / (3600 * 1000)
            ).alias("resolution_hours")
        ).filter(pl.col("resolution_hours") >= 0)

        if duration_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # Group and compute average hours
        return duration_df.group_by(group_cols).agg(
            pl.col("resolution_hours").mean().fill_null(0.0).alias(self.name)
        )
