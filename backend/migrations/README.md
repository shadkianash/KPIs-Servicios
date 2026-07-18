# Alembic Schema Migrations

This directory stores Alembic configuration scripts and the historical database migration revisions.

## Purpose
- Provide incremental, reproducible database migrations.
- Manage schema creation and indices generation on PostgreSQL safely.
- Keep the physical PostgreSQL database exactly in sync with the SQLAlchemy model representations defined in `app/models/`.
