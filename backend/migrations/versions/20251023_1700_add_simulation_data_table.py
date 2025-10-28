"""
Add simulation_data table for simulation persistence.

Revision ID: add_simulation_data_table
Revises: ec468c7d6085
Create Date: 2025-10-23 17:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision = "add_simulation_data_table"
down_revision = "ec468c7d6085"
branch_labels = None
depends_on = None


def _is_sqlite() -> bool:
    try:
        bind = op.get_bind()
        return bind.dialect.name == "sqlite"
    except Exception:
        return False


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Choose JSON type appropriate for the backend
    JSONType = sa.JSON
    if _is_sqlite():
        JSONType = sqlite.JSON
    else:
        # Prefer JSONB on Postgres for efficiency, but JSON is fine too
        JSONType = postgresql.JSONB

    tables = inspector.get_table_names()
    if "simulation_data" in tables:
        # Already exists (from previous manual setup) – skip creating
        return

    op.create_table(
        "simulation_data",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        # Configuration and context
        sa.Column("business_context", JSONType, nullable=True),
        sa.Column("questions_data", JSONType, nullable=True),
        sa.Column("simulation_config", JSONType, nullable=True),
        # Results
        sa.Column("personas", JSONType, nullable=True),
        sa.Column("interviews", JSONType, nullable=True),
        sa.Column("insights", JSONType, nullable=True),
        sa.Column("formatted_data", JSONType, nullable=True),
        # Metadata
        sa.Column("total_personas", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_interviews", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name="fk_sim_data_user_id"),
        sa.UniqueConstraint("simulation_id", name="uq_simulation_data_simulation_id"),
    )

    # Helpful index for lookups by simulation_id
    op.create_index(
        "ix_simulation_data_simulation_id",
        "simulation_data",
        ["simulation_id"],
        unique=True,
    )


def downgrade() -> None:
    # Drop index first, then table
    try:
        op.drop_index("ix_simulation_data_simulation_id", table_name="simulation_data")
    except Exception:
        pass
    op.drop_table("simulation_data")

