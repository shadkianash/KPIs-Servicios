# KPI Calculation and Analytics Engine

This document defines the architecture, design, and extensibility guidelines for the **KPI Calculation and Analytics Engine** of the Cyber Services Analytics Platform (CSAP).

---

## 1. High-Level KPI Engine Architecture

The analytics package (`app/analytics/`) runs as a fully decoupled, self-registering plug-in framework. It extracts operational database dimensions, instantiates high-performance **Polars DataFrames**, executes vectorized calculator formulas, and groups results into daily and monthly JSONB snapshots.

```text
       Operational Database
                 │
                 ▼ (Single Bulk Load)
         Polars DataFrames
                 │
                 ├─► [1. Data Validation] ──► Audit warnings (e.g. negative times)
                 │
                 ├─► [2. Execute Registered Calculators] ──► TicketsAssigned, SLA, Backlog, etc.
                 │
                 ├─► [3. Coalesce & Join Groups] ──► Reusable aggregators (Day, Month, Team, etc.)
                 │
                 └─► [4. Batch Load Snapshots] ──► Write to DailySnapshot / MonthlySnapshot
```

---

## 2. Generic KPI Calculator Interface

Every KPI must extend `BaseCalculator` (`app/analytics/core/base_calculator.py`) and declare:
- **`name`**: String key identifying the metric (e.g., `"tickets_assigned"`).
- **`description`**: Explanation of what the KPI represents.
- **`supported_aggregation_levels`**: List of levels where the metric is valid (e.g. `day`, `month`, `engineer`, `client`, `technology`, `team`, `global`).
- **`required_datasets`**: Map of source tables needed (e.g. `["tickets"]`, `["time_entries"]`, `["history"]`).
- **`calculation_version`**: Version tracker of the calculator formula.
- **`calculate(datasets, group_cols)`**: Pure vectorized computation returning a Polars DataFrame with the calculated metric.

---

## 3. Initial KPI Set

The platform calculates 10 distinct default metrics:

### Productivity
- **`tickets_assigned`**: Counts total tickets grouped by dimensions.
- **`tickets_closed`**: Counts tickets matching configurable terminal statuses.
- **`worked_hours`**: Sums logged work hours from time entries.
- **`avg_worked_hours_per_ticket`**: Calculates `worked_hours / tickets_closed`.

### SLA
- **`average_response_time`**: Measures elapsed hours between ticket creation and its first status change.
- **`average_resolution_time`**: Measures elapsed hours between ticket creation and terminal closure status.

### Backlog
- **`open_tickets`**: Counts active tickets currently in non-terminal states.
- **`reopened_tickets`**: Counts tickets transitioning from a terminal status back to an active status.

---

## 4. Reusable Aggregation Mappings

The engine groups operational dimensions horizontally across 7 customizable aggregation levels:
- **`day`**: Grouped on `snapshot_date`. Persisted in `DailySnapshot`.
- **`month`**: Grouped on `year` and `month`. Persisted in `MonthlySnapshot`.
- **`engineer`**: Grouped on `engineer_id`. Persisted in `MonthlySnapshot`.
- **`client`**: Grouped on `client_id`. Persisted in `MonthlySnapshot`.
- **`technology`**: Grouped on `technology_id`. Persisted in `MonthlySnapshot`.
- **`team`**: Grouped on `team_id`. Persisted in `MonthlySnapshot`.
- **`global`**: Unified across all records with zero group keys. Persisted in `MonthlySnapshot`.

---

## 5. Snapshot Strategy & Idempotency

### PostgreSQL JSONB Metrics Storage
Core analytical indices (date, year, month, engineer_id, client_id, technology_id, team_id, aggregation_level) are stored as explicit indexed database columns for query speed. However, all calculated metric values are stored in a flexible JSONB column named `metrics` (e.g., `{"tickets_assigned": 24, "worked_hours": 12.5}`).
This avoids database migrations when adding new KPIs in the future.

### Idempotent Recalculations
To support safe historical recalculations without duplicating data:
- Before inserting a new daily snapshot level, existing records in `DailySnapshot` are cleared.
- Before inserting a monthly or dimensional level, existing records for that specific aggregation level in `MonthlySnapshot` are cleared.

---

## 6. How to Add a New KPI Calculator

The engine discovers and executes registered calculators automatically. To add a new KPI:

1. **Write Calculator**: Create a new class extending `BaseCalculator` in `app/analytics/calculators/` and define its `calculate()` Polars expression.
2. **Register Calculator**: Add a single registration statement inside the bootstrap module (`app/analytics/core/registry_bootstrap.py`):
   ```python
   calculator_registry.register(MyNewKPICalculator())
   ```
3. **Execution**: The registry discovers it, and the `KPIEngine` will automatically execute, aggregate, and persist it into snapshots without further modifications.
