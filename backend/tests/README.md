# Pytest Test Suite

This directory contains the automated test suite for the FastAPI backend, utilizing Pytest.

## Structure
- `unit/`: Tests validating standalone functions, specifically the Polars KPI Calculation Engine (executed offline without active DB connections).
- `integration/`: Tests checking API routes, database repository layers, and ingestion flows against a live test Postgres/Redis instance.
- `conftest.py`: Shared pytest fixtures managing transactional databases isolation, mocked CSV streams, and test web client configurations.
