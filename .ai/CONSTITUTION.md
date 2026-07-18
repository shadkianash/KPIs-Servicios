# Code and Behavior Constitution

This Constitution outlines strict rules that guide how the CSAP codebase is developed and operated. Both AI and human developers must adhere to these tenets.

---

## Tenet 1: Single Source of Truth for Data Definitions
The database schema and Pydantic models are the strict single source of truth for all structured objects. No client-side modifications should be made that conflict with backend models.

## Tenet 2: Fail Loudly and Securely
- Never write empty `except` blocks. If an unexpected error occurs during data ingestion (e.g. malformed CSV from Archer), the system must log the detailed error and halt/fail gracefully instead of processing incomplete or corrupted datasets.
- Ensure that system exceptions do not leak raw server details or infrastructure variables to the frontend.

## Tenet 3: Zero-Dependency Domain Calculations
The analytical functions (KPI calculations via Polars) must remain completely free of database-specific logic or network framework integrations. They must process raw data structures/dataframes and return pure results. This allows testing calculations completely offline without database connections.

## Tenet 4: Explicit Over Implicit
Avoid magical abstractions. Do not use framework-specific decorators or libraries that perform automatic database transformations unless explicitly configured and documented under `docs/database/`.

## Tenet 5: Maintain Clean Commit Histories
Commits must be small, descriptive, and separate infrastructure/documentation changes from logic changes.
