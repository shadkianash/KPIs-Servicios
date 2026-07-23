# API Reference Documentation

This document serves as the comprehensive REST API reference for the **Cyber Services Analytics Platform (CSAP)**.

---

## Central Conventions & Response Envelopes

All versioned REST endpoints are prefix-mapped under `/api/v1/`. CSAP enforces strict success and error JSON envelopes to maintain consistency across backend delivery and frontend state parsing.

### 1. Success Response Envelope
All successful requests return a status code of `200 OK` and wrap the payload within a standard outer structure. If the payload is a paginated list, a `pagination` metadata block is included.

```json
{
  "success": true,
  "data": { ... },
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_records": 125,
    "total_pages": 3
  }
}
```

### 2. Error Response Envelope
All request errors, validation failures, and database lookup faults return standard HTTP status codes accompanied by a structured JSON error payload.

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "The requested resource could not be found.",
    "details": null
  }
}
```

---

## API Endpoints Catalog

### 1. Health Status
#### `GET /api/v1/analytics/health`
Returns the operational state of the KPI calculation engine.

* **Response Example:**
  ```json
  {
    "success": true,
    "data": {
      "status": "active",
      "engine_version": "1.0.0",
      "calculation_version": "1.0.0"
    },
    "pagination": null
  }
  ```

---

### 2. Active Catalogs (Metadata)
All catalog endpoints fetch lists of active master-dimension records used for drop-downs and lookup filtering in the client UI. Records where `is_active` is `false` are automatically excluded.

#### `GET /api/v1/metadata/clients`
#### `GET /api/v1/metadata/technologies`
#### `GET /api/v1/metadata/engineers`
#### `GET /api/v1/metadata/teams`

* **Query Parameters:**
  - `page` (integer, default: `1`): Pagination page.
  - `page_size` (integer, default: `50`, max: `100`): Records per page.
* **Response Example (Clients):**
  ```json
  {
    "success": true,
    "data": [
      { "id": "f5b8a05e-f00e-4ba9-b002-c94e9f783281", "name": "Client Acme" }
    ],
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total_records": 1,
      "total_pages": 1
    }
  }
  ```

---

### 3. KPI Calculations Execution History
Exposes audited execution jobs of the core Polars metric aggregation engine.

#### `GET /api/v1/kpi/executions`
Retrieves run logs sorted chronologically in descending order.

* **Query Parameters:**
  - `page` (integer, default: `1`): Pagination page.
  - `page_size` (integer, default: `50`, max: `100`): Records per page.

#### `GET /api/v1/kpi/executions/{execution_id}`
Retrieves complete details of a single calculation run, including processed volumes, parameters, warnings, or errors.

* **Path Parameters:**
  - `execution_id` (UUID): Unique run identifier.

---

### 4. Computed KPI Snapshots (Metrics)
Provides paginated, filterable access to aggregated analytical tables. Sorting is supported on both standard root attributes and nested metrics inside JSONB keys (e.g., `sort=-metrics.tickets_closed`).

#### `GET /api/v1/kpi/daily`
Retrieves daily KPI metrics snapshots.

* **Query Parameters:**
  - `start_date` (string, `YYYY-MM-DD`): Filter records on or after date.
  - `end_date` (string, `YYYY-MM-DD`): Filter records on or before date.
  - `engineer_id` (string): Filter by assigned engineer uuid.
  - `client_id` (string): Filter by target client uuid.
  - `technology_id` (string): Filter by technology uuid.
  - `team_id` (string): Filter by desk team uuid.
  - `sort` (string): Column or nested metric path (e.g., `-snapshot_date`, `metrics.worked_hours`).
  - `page` / `page_size`

#### `GET /api/v1/kpi/monthly`
Retrieves monthly KPI metrics snapshots.

* **Query Parameters:**
  - `year` (integer): Filter by year (e.g. `2026`).
  - `month` (integer): Filter by month (`1`-`12`).
  - `engineer_id` / `client_id` / `technology_id` / `team_id` / `sort` / `page` / `page_size`

---

### 5. Historical Evolution (Drill-downs)
Tracks historical trend parameters for a single dimension entity across consecutive periods.

#### `GET /api/v1/drilldown/engineer/{engineer_id}`
#### `GET /api/v1/drilldown/client/{client_id}`
#### `GET /api/v1/drilldown/technology/{technology_id}`
#### `GET /api/v1/drilldown/team/{team_id}`

* **Path Parameters:**
  - `entity_id` (string): Dimension ID.
* **Query Parameters:**
  - `type` (string, default: `"monthly"`): Resolution level, either `"daily"` or `"monthly"`.
  - `page` / `page_size`
