from app.analytics.calculators.backlog import (
    OpenTicketsCalculator,
    ReopenedTicketsCalculator,
)
from app.analytics.calculators.productivity import (
    AvgWorkedHoursCalculator,
    TicketsAssignedCalculator,
    TicketsClosedCalculator,
    WorkedHoursCalculator,
)
from app.analytics.calculators.sla import (
    FirstResponseTimeCalculator,
    ResolutionTimeCalculator,
)
from app.analytics.core.registry import calculator_registry


def bootstrap_registry() -> None:
    """Discovers and registers all built-in concrete KPI calculators."""
    calculator_registry.register(TicketsAssignedCalculator())
    calculator_registry.register(TicketsClosedCalculator())
    calculator_registry.register(WorkedHoursCalculator())
    calculator_registry.register(AvgWorkedHoursCalculator())
    calculator_registry.register(FirstResponseTimeCalculator())
    calculator_registry.register(ResolutionTimeCalculator())
    calculator_registry.register(OpenTicketsCalculator())
    calculator_registry.register(ReopenedTicketsCalculator())
