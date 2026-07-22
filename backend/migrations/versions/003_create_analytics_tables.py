"""create analytics tables

Revision ID: 003_create_analytics_tables
Revises: 002_create_operational_tables
Create Date: 2026-03-05 02:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_create_analytics_tables"
down_revision: str | None = "002_create_operational_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create kpi_executions table
    op.create_table(
        "kpi_executions",
        sa.Column("execution_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("execution_status", sa.String(length=20), nullable=False),
        sa.Column("calculation_version", sa.String(length=20), nullable=False),
        sa.Column("engine_version", sa.String(length=20), nullable=False),
        sa.Column("processed_tickets", sa.Integer(), nullable=False),
        sa.Column("processed_time_entries", sa.Integer(), nullable=False),
        sa.Column("generated_daily_snapshots", sa.Integer(), nullable=False),
        sa.Column("generated_monthly_snapshots", sa.Integer(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("errors", sa.JSON(), nullable=True),
        sa.Column("correlation_id", sa.String(length=50), nullable=False),
        sa.Column("source_import_job_ids", sa.JSON(), nullable=True),
        sa.Column("execution_parameters", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("execution_id", name="pk_kpi_executions"),
    )
    op.create_index(
        "ix_kpi_executions_correlation_id",
        "kpi_executions",
        ["correlation_id"],
        unique=False,
    )

    # 2. Create daily_snapshots table
    op.create_table(
        "daily_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(), nullable=False),
        sa.Column("aggregation_level", sa.String(length=20), nullable=False),
        sa.Column("engineer_id", sa.String(length=100), nullable=True),
        sa.Column("client_id", sa.String(length=100), nullable=True),
        sa.Column("technology_id", sa.String(length=100), nullable=True),
        sa.Column("team_id", sa.String(length=100), nullable=True),
        sa.Column("snapshot_version", sa.String(length=20), nullable=False),
        sa.Column("execution_id", sa.Uuid(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["kpi_executions.execution_id"],
            name="fk_daily_snapshots_execution_id_kpi_executions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_daily_snapshots"),
    )
    op.create_index(
        "ix_daily_snapshots_aggregation_level",
        "daily_snapshots",
        ["aggregation_level"],
        unique=False,
    )
    op.create_index(
        "ix_daily_snapshots_client_id", "daily_snapshots", ["client_id"], unique=False
    )
    op.create_index(
        "ix_daily_snapshots_engineer_id",
        "daily_snapshots",
        ["engineer_id"],
        unique=False,
    )
    op.create_index(
        "ix_daily_snapshots_execution_id",
        "daily_snapshots",
        ["execution_id"],
        unique=False,
    )
    op.create_index(
        "ix_daily_snapshots_snapshot_date",
        "daily_snapshots",
        ["snapshot_date"],
        unique=False,
    )
    op.create_index(
        "ix_daily_snapshots_team_id", "daily_snapshots", ["team_id"], unique=False
    )
    op.create_index(
        "ix_daily_snapshots_technology_id",
        "daily_snapshots",
        ["technology_id"],
        unique=False,
    )

    # 3. Create monthly_snapshots table
    op.create_table(
        "monthly_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("aggregation_level", sa.String(length=20), nullable=False),
        sa.Column("engineer_id", sa.String(length=100), nullable=True),
        sa.Column("client_id", sa.String(length=100), nullable=True),
        sa.Column("technology_id", sa.String(length=100), nullable=True),
        sa.Column("team_id", sa.String(length=100), nullable=True),
        sa.Column("snapshot_version", sa.String(length=20), nullable=False),
        sa.Column("execution_id", sa.Uuid(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["kpi_executions.execution_id"],
            name="fk_monthly_snapshots_execution_id_kpi_executions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_monthly_snapshots"),
    )
    op.create_index(
        "ix_monthly_snapshots_aggregation_level",
        "monthly_snapshots",
        ["aggregation_level"],
        unique=False,
    )
    op.create_index(
        "ix_monthly_snapshots_client_id",
        "monthly_snapshots",
        ["client_id"],
        unique=False,
    )
    op.create_index(
        "ix_monthly_snapshots_engineer_id",
        "monthly_snapshots",
        ["engineer_id"],
        unique=False,
    )
    op.create_index(
        "ix_monthly_snapshots_execution_id",
        "monthly_snapshots",
        ["execution_id"],
        unique=False,
    )
    op.create_index(
        "ix_monthly_snapshots_month", "monthly_snapshots", ["month"], unique=False
    )
    op.create_index(
        "ix_monthly_snapshots_team_id", "monthly_snapshots", ["team_id"], unique=False
    )
    op.create_index(
        "ix_monthly_snapshots_technology_id",
        "monthly_snapshots",
        ["technology_id"],
        unique=False,
    )
    op.create_index(
        "ix_monthly_snapshots_year", "monthly_snapshots", ["year"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_monthly_snapshots_year", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_technology_id", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_team_id", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_month", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_execution_id", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_engineer_id", table_name="monthly_snapshots")
    op.drop_index("ix_monthly_snapshots_client_id", table_name="monthly_snapshots")
    op.drop_index(
        "ix_monthly_snapshots_aggregation_level", table_name="monthly_snapshots"
    )
    op.drop_table("monthly_snapshots")

    op.drop_index("ix_daily_snapshots_technology_id", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_team_id", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_snapshot_date", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_execution_id", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_engineer_id", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_client_id", table_name="daily_snapshots")
    op.drop_index("ix_daily_snapshots_aggregation_level", table_name="daily_snapshots")
    op.drop_table("daily_snapshots")

    op.drop_index("ix_kpi_executions_correlation_id", table_name="kpi_executions")
    op.drop_table("kpi_executions")
