"""create operational and sync tables

Revision ID: 002_create_operational_tables
Revises: 001_create_staging_tables
Create Date: 2026-03-05 01:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_create_operational_tables"
down_revision: str | None = "001_create_staging_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_clients"),
    )
    op.create_index("ix_clients_name", "clients", ["name"], unique=True)

    # 2. Create engineers table
    op.create_table(
        "engineers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_engineers"),
    )
    op.create_index("ix_engineers_name", "engineers", ["name"], unique=True)

    # 3. Create technologies table
    op.create_table(
        "technologies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_technologies"),
    )
    op.create_index("ix_technologies_name", "technologies", ["name"], unique=True)

    # 4. Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_teams"),
    )
    op.create_index("ix_teams_name", "teams", ["name"], unique=True)

    # 5. Create tickets table
    op.create_table(
        "tickets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticket_id_archer", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=True),
        sa.Column("closed_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("client_id", sa.Uuid(), nullable=True),
        sa.Column("engineer_id", sa.Uuid(), nullable=True),
        sa.Column("technology_id", sa.Uuid(), nullable=True),
        sa.Column("team_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name="fk_tickets_client_id_clients",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["engineer_id"],
            ["engineers.id"],
            name="fk_tickets_engineer_id_engineers",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
            name="fk_tickets_team_id_teams",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["technology_id"],
            ["technologies.id"],
            name="fk_tickets_technology_id_technologies",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tickets"),
    )
    op.create_index("ix_tickets_client_id", "tickets", ["client_id"], unique=False)
    op.create_index("ix_tickets_engineer_id", "tickets", ["engineer_id"], unique=False)
    op.create_index("ix_tickets_team_id", "tickets", ["team_id"], unique=False)
    op.create_index(
        "ix_tickets_technology_id", "tickets", ["technology_id"], unique=False
    )
    op.create_index(
        "ix_tickets_ticket_id_archer", "tickets", ["ticket_id_archer"], unique=True
    )

    # 6. Create ticket_history table
    op.create_table(
        "ticket_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("history_id_archer", sa.String(length=100), nullable=False),
        sa.Column("ticket_id", sa.String(length=100), nullable=False),
        sa.Column("change_date", sa.DateTime(), nullable=True),
        sa.Column("field_changed", sa.String(length=100), nullable=True),
        sa.Column("old_value", sa.String(), nullable=True),
        sa.Column("new_value", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.ticket_id_archer"],
            name="fk_ticket_history_ticket_id_tickets",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ticket_history"),
    )
    op.create_index(
        "ix_ticket_history_history_id_archer",
        "ticket_history",
        ["history_id_archer"],
        unique=True,
    )
    op.create_index(
        "ix_ticket_history_ticket_id", "ticket_history", ["ticket_id"], unique=False
    )

    # 7. Create time_entries table
    op.create_table(
        "time_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("entry_id_archer", sa.String(length=100), nullable=False),
        sa.Column("ticket_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("work_date", sa.DateTime(), nullable=True),
        sa.Column("hours_spent", sa.Float(), nullable=True),
        sa.Column("activity_type", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.ticket_id_archer"],
            name="fk_time_entries_ticket_id_tickets",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_time_entries"),
    )
    op.create_index(
        "ix_time_entries_entry_id_archer",
        "time_entries",
        ["entry_id_archer"],
        unique=True,
    )
    op.create_index(
        "ix_time_entries_ticket_id", "time_entries", ["ticket_id"], unique=False
    )

    # 8. Create sync_jobs table
    op.create_table(
        "sync_jobs",
        sa.Column("sync_id", sa.Uuid(), nullable=False),
        sa.Column("import_job_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("inserted_records", sa.Integer(), nullable=False),
        sa.Column("updated_records", sa.Integer(), nullable=False),
        sa.Column("unchanged_records", sa.Integer(), nullable=False),
        sa.Column("rejected_records", sa.Integer(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("errors", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("correlation_id", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["import_job_id"],
            ["import_jobs.job_id"],
            name="fk_sync_jobs_import_job_id_import_jobs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("sync_id", name="pk_sync_jobs"),
    )
    op.create_index(
        "ix_sync_jobs_correlation_id", "sync_jobs", ["correlation_id"], unique=False
    )
    op.create_index(
        "ix_sync_jobs_import_job_id", "sync_jobs", ["import_job_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_sync_jobs_import_job_id", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_correlation_id", table_name="sync_jobs")
    op.drop_table("sync_jobs")

    op.drop_index("ix_time_entries_ticket_id", table_name="time_entries")
    op.drop_index("ix_time_entries_entry_id_archer", table_name="time_entries")
    op.drop_table("time_entries")

    op.drop_index("ix_ticket_history_ticket_id", table_name="ticket_history")
    op.drop_index("ix_ticket_history_history_id_archer", table_name="ticket_history")
    op.drop_table("ticket_history")

    op.drop_index("ix_tickets_ticket_id_archer", table_name="tickets")
    op.drop_index("ix_tickets_technology_id", table_name="tickets")
    op.drop_index("ix_tickets_team_id", table_name="tickets")
    op.drop_index("ix_tickets_engineer_id", table_name="tickets")
    op.drop_index("ix_tickets_client_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_index("ix_teams_name", table_name="teams")
    op.drop_table("teams")

    op.drop_index("ix_technologies_name", table_name="technologies")
    op.drop_table("technologies")

    op.drop_index("ix_engineers_name", table_name="engineers")
    op.drop_table("engineers")

    op.drop_index("ix_clients_name", table_name="clients")
    op.drop_table("clients")
