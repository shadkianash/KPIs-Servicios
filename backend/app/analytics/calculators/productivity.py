import polars as pl

from app.analytics.core.base_calculator import BaseCalculator


class TicketsAssignedCalculator(BaseCalculator):
    """Calculates the total number of tickets assigned."""

    @property
    def name(self) -> str:
        return "tickets_assigned"

    @property
    def description(self) -> str:
        return "Total number of service tickets assigned."

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        tickets_df = datasets["tickets"]
        if tickets_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Int64},
            )

        # Vectorized group_by length
        return tickets_df.group_by(group_cols).agg(pl.len().alias(self.name))


class TicketsClosedCalculator(BaseCalculator):
    """Calculates the total number of closed tickets based on terminal statuses."""

    def __init__(self, terminal_statuses: list[str] | None = None) -> None:
        # Configuration-driven terminal statuses (no hardcoding!)
        self.terminal_statuses = terminal_statuses or ["Closed", "Resolved"]

    @property
    def name(self) -> str:
        return "tickets_closed"

    @property
    def description(self) -> str:
        return "Total number of service tickets closed."

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        tickets_df = datasets["tickets"]
        if tickets_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Int64},
            )

        # Filter by configurable terminal statuses
        closed_df = tickets_df.filter(pl.col("status").is_in(self.terminal_statuses))
        return closed_df.group_by(group_cols).agg(pl.len().alias(self.name))


class WorkedHoursCalculator(BaseCalculator):
    """Calculates the total worked hours from time entries."""

    @property
    def name(self) -> str:
        return "worked_hours"

    @property
    def description(self) -> str:
        return "Total logged worked hours on tickets."

    @property
    def required_datasets(self) -> list[str]:
        return ["time_entries"]

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        time_df = datasets["time_entries"]
        if time_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        # Group and sum hours spent safely
        return time_df.group_by(group_cols).agg(
            pl.col("hours_spent").sum().fill_null(0.0).alias(self.name)
        )


class AvgWorkedHoursCalculator(BaseCalculator):
    """Calculates the average worked hours per closed ticket."""

    def __init__(self, terminal_statuses: list[str] | None = None) -> None:
        self.closed_calc = TicketsClosedCalculator(terminal_statuses)
        self.hours_calc = WorkedHoursCalculator()

    @property
    def name(self) -> str:
        return "avg_worked_hours_per_ticket"

    @property
    def description(self) -> str:
        return "Average worked hours logged per closed ticket."

    @property
    def required_datasets(self) -> list[str]:
        return ["tickets", "time_entries"]

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        closed_df = self.closed_calc.calculate(datasets, group_cols)
        hours_df = self.hours_calc.calculate(datasets, group_cols)

        # Merge results using a vectorized inner/outer join on aggregation group cols
        if closed_df.is_empty() or hours_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Float64},
            )

        if not group_cols:
            merged = pl.concat([closed_df, hours_df], how="horizontal_extend")
        else:
            merged = closed_df.join(hours_df, on=group_cols, how="full")

        # Divide hours by closed count, with 0 division checks
        result_df = merged.with_columns(
            pl.when(pl.col("tickets_closed") > 0)
            .then(pl.col("worked_hours") / pl.col("tickets_closed"))
            .otherwise(0.0)
            .alias(self.name)
        )

        return result_df.select(group_cols + [self.name])
