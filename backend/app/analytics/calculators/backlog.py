import polars as pl

from app.analytics.core.base_calculator import BaseCalculator


class OpenTicketsCalculator(BaseCalculator):
    """Calculates the number of active, open tickets (non-terminal states)."""

    def __init__(self, terminal_statuses: list[str] | None = None) -> None:
        self.terminal_statuses = terminal_statuses or ["Closed", "Resolved"]

    @property
    def name(self) -> str:
        return "open_tickets"

    @property
    def description(self) -> str:
        return "Total number of active, non-closed service tickets."

    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        tickets_df = datasets["tickets"]
        if tickets_df.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Int64},
            )

        # Filter active non-closed tickets
        open_df = tickets_df.filter(
            ~pl.col("status").is_in(self.terminal_statuses)
            | pl.col("closed_date").is_null()
        )
        return open_df.group_by(group_cols).agg(pl.len().alias(self.name))


class ReopenedTicketsCalculator(BaseCalculator):
    """Calculates tickets transitioning terminal back to active status."""

    def __init__(
        self,
        active_statuses: list[str] | None = None,
        terminal_statuses: list[str] | None = None,
    ) -> None:
        self.active_statuses = active_statuses or ["New", "In Progress", "Reopened"]
        self.terminal_statuses = terminal_statuses or ["Closed", "Resolved"]

    @property
    def name(self) -> str:
        return "reopened_tickets"

    @property
    def description(self) -> str:
        return "Count of tickets transitioning from terminal back to active state."

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
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Int64},
            )

        # 1. Filter history for transitions from terminal back to active status
        reopened_history = history_df.filter(
            (pl.col("field_changed") == "status")
            & (pl.col("old_value").is_in(self.terminal_statuses))
            & (pl.col("new_value").is_in(self.active_statuses))
        )

        if reopened_history.is_empty():
            return pl.DataFrame(
                {col: [] for col in group_cols + [self.name]},
                schema=dict.fromkeys(group_cols, pl.String) | {self.name: pl.Int64},
            )

        # Find distinct ticket IDs that were reopened
        reopened_ids = reopened_history.select(pl.col("ticket_id").unique())

        # 2. Join with Tickets to retain correct group attributes
        joined = tickets_df.join(
            reopened_ids,
            left_on="ticket_id_archer",
            right_on="ticket_id",
            how="inner",
        )

        # 3. Group and count
        return joined.group_by(group_cols).agg(pl.len().alias(self.name))
