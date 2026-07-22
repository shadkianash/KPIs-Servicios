"""create staging and import jobs tables

Revision ID: 001_create_staging_tables
Revises:
Create Date: 2026-03-05 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_create_staging_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create import_jobs table
    op.create_table(
        "import_jobs",
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("import_batch_id", sa.Uuid(), nullable=False),
        sa.Column("source_system", sa.String(length=50), nullable=False),
        sa.Column("connector_name", sa.String(length=50), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("processed_rows", sa.Integer(), nullable=False),
        sa.Column("imported_rows", sa.Integer(), nullable=False),
        sa.Column("updated_rows", sa.Integer(), nullable=False),
        sa.Column("skipped_rows", sa.Integer(), nullable=False),
        sa.Column("duplicated_rows", sa.Integer(), nullable=False),
        sa.Column("invalid_rows", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("importer_version", sa.String(length=20), nullable=False),
        sa.Column("correlation_id", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("job_id", name="pk_import_jobs"),
    )
    op.create_index(
        "ix_import_jobs_correlation_id",
        "import_jobs",
        ["correlation_id"],
        unique=False,
    )
    op.create_index(
        "ix_import_jobs_import_batch_id",
        "import_jobs",
        ["import_batch_id"],
        unique=False,
    )
    op.create_index(
        "uq_import_jobs_checksum_sha256",
        "import_jobs",
        ["checksum_sha256"],
        unique=True,
    )

    # 2. Create staging_ticket_details table
    op.create_table(
        "staging_ticket_details",
        sa.Column("staging_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("ticket_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=True),
        sa.Column("closed_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("assigned_team", sa.String(length=100), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("synchronized_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["import_jobs.job_id"],
            name="fk_staging_ticket_details_job_id_import_jobs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("staging_id", name="pk_staging_ticket_details"),
    )
    op.create_index(
        "ix_staging_ticket_details_job_id",
        "staging_ticket_details",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        "ix_staging_ticket_details_ticket_id",
        "staging_ticket_details",
        ["ticket_id"],
        unique=False,
    )

    # 3. Create staging_ticket_history table
    op.create_table(
        "staging_ticket_history",
        sa.Column("staging_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("history_id", sa.String(length=100), nullable=False),
        sa.Column("ticket_id", sa.String(length=100), nullable=False),
        sa.Column("change_date", sa.DateTime(), nullable=True),
        sa.Column("field_changed", sa.String(length=100), nullable=True),
        sa.Column("old_value", sa.String(), nullable=True),
        sa.Column("new_value", sa.String(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("synchronized_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["import_jobs.job_id"],
            name="fk_staging_ticket_history_job_id_import_jobs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("staging_id", name="pk_staging_ticket_history"),
    )
    op.create_index(
        "ix_staging_ticket_history_job_id",
        "staging_ticket_history",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        "ix_staging_ticket_history_history_id",
        "staging_ticket_history",
        ["history_id"],
        unique=False,
    )
    op.create_index(
        "ix_staging_ticket_history_ticket_id",
        "staging_ticket_history",
        ["ticket_id"],
        unique=False,
    )

    # 4. Create staging_time_entries table
    op.create_table(
        "staging_time_entries",
        sa.Column("staging_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("entry_id", sa.String(length=100), nullable=False),
        sa.Column("ticket_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("work_date", sa.DateTime(), nullable=True),
        sa.Column("hours_spent", sa.Float(), nullable=True),
        sa.Column("activity_type", sa.String(length=100), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("synchronized_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["import_jobs.job_id"],
            name="fk_staging_time_entries_job_id_import_jobs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("staging_id", name="pk_staging_time_entries"),
    )
    op.create_index(
        "ix_staging_time_entries_job_id",
        "staging_time_entries",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        "ix_staging_time_entries_entry_id",
        "staging_time_entries",
        ["entry_id"],
        unique=False,
    )
    op.create_index(
        "ix_staging_time_entries_ticket_id",
        "staging_time_entries",
        ["ticket_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_staging_time_entries_ticket_id", table_name="staging_time_entries"
    )
    op.drop_index("ix_staging_time_entries_entry_id", table_name="staging_time_entries")
    op.drop_index("ix_staging_time_entries_job_id", table_name="staging_time_entries")
    op.drop_table("staging_time_entries")

    op.drop_index(
        "ix_staging_ticket_history_ticket_id", table_name="staging_ticket_history"
    )
    op.drop_index(
        "ix_staging_ticket_history_history_id", table_name="staging_ticket_history"
    )
    op.drop_index(
        "ix_staging_ticket_history_job_id", table_name="staging_ticket_history"
    )
    op.drop_table("staging_ticket_history")

    op.drop_index(
        "ix_staging_ticket_details_ticket_id", table_name="staging_ticket_details"
    )
    op.drop_index(
        "ix_staging_ticket_details_job_id", table_name="staging_ticket_details"
    )
    op.drop_table("staging_ticket_details")

    op.drop_index("uq_import_jobs_checksum_sha256", table_name="import_jobs")
    op.drop_index("ix_import_jobs_import_batch_id", table_name="import_jobs")
    op.drop_index("ix_import_jobs_correlation_id", table_name="import_jobs")
    op.drop_table("import_jobs")
