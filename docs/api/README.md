# API Reference Documentation

This folder documents the REST API contract exposed by the FastAPI backend, utilized by the React frontend and potential external consumers.

---

## Expected Content & Scope

- **Endpoints Reference**: Detailed descriptions of paths, HTTP methods, request headers, query parameters, and JSON payloads.
- **Error Handling**: Mapping of HTTP status codes and standard JSON error response structures.
- **Authentication**: JWT authentication flow and route authorization rules.
- **Rate Limiting**: Operational limits enforced on API endpoints via Redis.

---

## API Conventions

1. **RESTful Paths**: Paths must use lowercase and hyphen-separated names (e.g., `/api/v1/kpis/sla-compliance`).
2. **Versioned Routes**: All public API endpoints must be versioned, starting with `/api/v1/`.
3. **Consistent Envelope**: Error responses must follow a consistent layout:
   ```json
   {
     "success": false,
     "error": {
       "code": "VALIDATION_FAILED",
       "message": "Detailed explanation of fields that failed validation",
       "details": []
     }
   }
   ```

---

## Example Endpoint Definition

### `GET /api/v1/kpis/sla-compliance`

Returns the calculated SLA compliance rate for a given team over a specified timeframe.

#### Query Parameters
- `team_id` (string, required): Unique identifier of the target service desk team.
- `start_date` (string, ISO-8601, required): Filter start date (e.g. `2026-01-01`).
- `end_date` (string, ISO-8601, required): Filter end date (e.g. `2026-01-31`).

#### Response Example (`200 OK`)
```json
{
  "success": true,
  "data": {
    "team_id": "secoops-t1",
    "team_name": "Security Operations Tier 1",
    "compliance_rate": 94.2,
    "total_resolved": 1250,
    "sla_met": 1178,
    "sla_breached": 72
  }
}
```
