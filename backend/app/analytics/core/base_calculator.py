from abc import ABC, abstractmethod

import polars as pl


class BaseCalculator(ABC):
    """Abstract base class for all plug-in KPI calculators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier of the KPI (e.g. 'tickets_assigned')."""

    @property
    @abstractmethod
    def description(self) -> str:
        """A descriptive explanation of the calculated metric."""

    @property
    def supported_aggregation_levels(self) -> list[str]:
        """Levels supported by this calculator (e.g. 'team', 'engineer')."""
        return ["day", "month", "engineer", "client", "technology", "team", "global"]

    @property
    def required_datasets(self) -> list[str]:
        """Names of operational datasets required for this calculation."""
        return ["tickets"]

    @property
    def calculation_version(self) -> str:
        """Standard version tracking string for this specific logic."""
        return "1.0.0"

    @abstractmethod
    def calculate(
        self, datasets: dict[str, pl.DataFrame], group_cols: list[str]
    ) -> pl.DataFrame:
        """Vectorized computation of the metric on Polars DataFrames.

        Args:
            datasets: Dict of loaded Polars DataFrames ('tickets', 'history', etc.).
            group_cols: List of column names to group/aggregate by.

        Returns:
            A Polars DataFrame containing group columns and a single column
            matching self.name.
        """
