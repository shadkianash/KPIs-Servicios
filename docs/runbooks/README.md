# System Runbooks & Operations

This folder contains functional operational guides to compile, build, run, test, and deploy the Cyber Services Analytics Platform (CSAP).

---

## Expected Content & Scope

- **Local Setup Runbook**: Direct instructions on how to clone, install dependencies, and start local development servers.
- **Testing Runbook**: Commands and strategies for executing Python tests (Pytest), React unit tests (Vitest), and browser automation tests (Playwright).
- **Ingestion Execution Runbook**: How to manually trigger the daily Archer CSV ingestion process.
- **Troubleshooting Runbook**: Common issue logs, database migration recoveries, and container restart procedures.

---

## Operational Conventions

1. **Dockerized Environment**: The default development cycle is managed via Docker Compose to ensure a identical environment setup across teams.
2. **Environment Variables**: Sensitive credentials (database passwords, API keys) must be loaded from external `.env` files. **Never** hardcode credentials in any script or codebase file.

---

## Example Ingest Runbook Entry

### Manually Ingesting a Daily Archer Export CSV

In cases where the automated scheduler fails, operational administrators can trigger manual CSV ingestion using the CLI tool bundled with the FastAPI container:

1. Copy the raw CSV export file into the ingestion workspace folder:
   ```bash
   cp ~/Downloads/archer_export_2026_03_05.csv ./infra/storage/ingress/
   ```
2. Exec into the running backend API container:
   ```bash
   docker compose exec backend bash
   ```
3. Execute the CLI command passing the filename:
   ```bash
   python -m app.cli.ingest --file /app/storage/ingress/archer_export_2026_03_05.csv
   ```
4. Verify stdout displays success and the number of records imported:
   ```text
   [INFO] Ingestion started for file: archer_export_2026_03_05.csv
   [INFO] Successfully parsed 12,450 rows via Polars engine.
   [INFO] Data successfully committed to Database. 0 violations encountered.
   ```
