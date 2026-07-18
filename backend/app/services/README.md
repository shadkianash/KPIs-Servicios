# Business Logic Services & Polars Engine

This folder contains the core business intelligence services, metric calculation functions, and domain controllers.

## Purpose
- Implement transactional operations and business orchestration rules.
- Host the **Polars KPI Calculation Engine**, which calculates backlog sizing, ticket aging categories, and SLA compliance metrics.

## Architecture Rule
- Calculation services must be designed to be completely database-agnostic. They process data structures/dataframes and return computed data schemas, making them 100% testable without database side effects.
