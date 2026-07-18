# Architecture Design Documentation

This folder contains architectural designs, systemic decisions, and operational structure mappings for CSAP.

---

## Expected Content & Scope

- **High-Level Diagrams**: C4 Model diagrams or simple ASCII/Mermaid flows describing boundaries.
- **Data Loaders Strategy**: In-depth explanations of how Archer CSV imports are designed via an abstract loader interface to allow seamless plugability for future APIs (Jira, ServiceNow, custom endpoints).
- **KPI Engine Specifications**: Mathematical formulas, data mapping, and execution instructions for the Polars core engine.
- **Caching Policies**: Detailed explanation of when and how Redis is used to cache heavy historical trend calculations.

---

## Architectural Conventions

1. **Decoupled Business Logic**: Under no circumstance should database queries, HTTP requests, or schema validation be bundled directly inside the calculation code.
2. **Stateless Service Layer**: Services must not hold in-memory request-specific state. State must reside in either the persistent DB (Postgres) or cache (Redis).
3. **Pydantic Validation**: All data moving across system boundaries (API Requests, CSV Ingestion, API Responses) must be parsed and verified by Pydantic v2 schemas.

---

## Design Pattern Example: Abstract Data Loader

Below is an architectural template for adding new data adapters to the platform:

```python
from typing import Protocol
import polars as pl

class ServiceDataLoader(Protocol):
    def fetch_raw_data(self) -> pl.DataFrame:
        """Fetch raw tabular data from the target service."""
        ...

    def transform_to_standard_schema(self, df: pl.DataFrame) -> pl.DataFrame:
        """Enforce standard columns: ticket_id, create_date, close_date, status, team."""
        ...
```
