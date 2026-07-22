from app.analytics.core.base_calculator import BaseCalculator


class CalculatorRegistry:
    """Registry pattern that discovers and exposes plug-in KPI calculators."""

    def __init__(self) -> None:
        self._calculators: dict[str, BaseCalculator] = {}

    def register(self, calculator: BaseCalculator) -> None:
        """Register a new KPI calculator."""
        self._calculators[calculator.name] = calculator

    def get_calculators(self) -> list[BaseCalculator]:
        """Get all registered calculators."""
        return list(self._calculators.values())


# Global singleton instance
calculator_registry = CalculatorRegistry()
