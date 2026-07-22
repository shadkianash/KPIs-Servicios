# Production Data Synchronization Engine

This document defines the architecture, strategies, and operational recovery runbooks for the **Production Data Synchronization Engine** of the Cyber Services Analytics Platform (CSAP).

---

## 1. High-Level Synchronization Architecture

The synchronization engine operates downstream from our staging ingest tables. It is responsible for mapping, normalizing, validating, and upserting data from staging tables (`staging_ticket_details`, `staging_ticket_history`, `staging_time_entries`) into clean operational schemas.

```text
  Staging Records
        │
        ▼
┌──────────────────────────────┐
│  SynchronizationService      │
└──────────────────────────────┘
        │
        ├─► [1. Resolve Master Data] ──► Team, Client, Engineer, Tech
        │
        ├─► [2. Apply Change Detector] ──► Only update if operational != staging
        │
        ├─► [3. Conflict Resolution] ──► SOURCE_WINS, DATABASE_WINS, MOST_RECENT
        │
        └─► [4. Validate Referential] ──► Block orphaned history or time entries
                │
                ▼ (Transactional Savepoint Nested Commit)
      Operational DB Model
```

---

## 2. Abstractions

The sync framework contains several modular and extensible components:

1. **`SyncJob`**: Tracks the run duration, started/finished times, insertion, update, rejection counts, audit warning logs, and status (`RUNNING`, `COMPLETED`, `FAILED`).
2. **`SynchronizationContext`**: Governs conflict strategies and dimensional resolver preferences.
3. **`SynchronizationResult`**: Holds execution diagnostics, warnings, and errors.
4. **`ChangeDetector`**: Evaluates field-level diffs to prevent redundant database modifications.
5. **`MasterDataResolver`**: Performs localized caching and master entity lookups.
6. **`SynchronizationService`**: Manages the main synchronization process.

---

## 3. Change Detection Strategy

To maximize query performance and avoid unnecessary database writes:
- We compare the attributes of an existing operational record (e.g. `Ticket`) with incoming staging record fields.
- Updates are bypassed if values are identical.
- If they differ, only changed attributes are overwritten.
- A change summary detailing `"old"` vs `"new"` values is recorded for audibility.

---

## 4. Conflict Resolution

When values collide between the source import file and the existing operational database records, one of several configurable strategies is applied:

- **`SOURCE_WINS`** (Default): Overwrites operational fields with incoming values.
- **`DATABASE_WINS`**: Retains existing operational database records, ignoring the incoming values.
- **`MOST_RECENT`**: Evaluates modifying timestamps, applying values from the record with the most recent modify date.
- **`IGNORE`**: Completely skips modification of existing records.

---

## 5. Master Data Resolution

Resolvers are provided for **Client**, **Engineer**, **Technology**, and **Team**.
When a referenced dimensional name is not present in the system, its behavior is determined by configurable resolver strategies:

- **`CREATE_IF_MISSING`** (Default): Automatically creates the missing dimension, flushes its primary key to SQL, caches it, and associates it with the ticket.
- **`REJECT_IF_MISSING`**: Rejects the record from being loaded, logging an audit error.
- **`WARNING_ONLY`**: Logs an auditable warning and proceeds with a null reference.

---

## 6. Referential Integrity & Idempotency

### Prevent Orphans
Every relationship is validated prior to insertion. Staging `history` and staging `time` logs are checked against existing operational tickets. If a staging item references a `ticket_id_archer` that is not loaded, the record is rejected, and an error is registered in the sync audit trail.

### Idempotency
Double synchronization execution produces zero duplicate rows. Unique business key restrictions (`ticket_id_archer`, `history_id_archer`, `entry_id_archer`) are checked against existing values to verify if a record has already been synchronized, making the pipeline completely idempotent.

---

## 7. Transaction Model & Recovery

Every execution is isolated in an **explicit nested database transaction savepoint** (`session.begin_nested()`).
- If a fatal error occurs during execution, the savepoint rolls back all operational table updates.
- Staging data remains completely untouched and preserved.
- The outer transaction commits the sync status as `FAILED` alongside full traceback errors in the `sync_jobs` audit table.

### Recovery Process
1. Inspect the `sync_jobs` audit error log:
   ```sql
   SELECT errors FROM sync_jobs WHERE status = 'FAILED' ORDER BY started_at DESC LIMIT 1;
   ```
2. Resolve the underlying referential, format, or master data issue.
3. Re-trigger synchronization for the respective `import_job_id`. Since the synchronization engine is completely idempotent, it will skip already sync'd rows and successfully process the remainder.
