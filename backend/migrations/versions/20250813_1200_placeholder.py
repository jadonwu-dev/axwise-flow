"""Placeholder migration to bridge missing revision in production

Revision ID: 20250813_1200
Revises: 20250812_1400
Create Date: 2025-08-13 12:00:00.000000

This migration intentionally does nothing. It exists to reconcile environments
where the revision '20250813_1200' was stamped/applied, but the script is
missing in the repository.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250813_1200"
down_revision = "20250812_1400"
branch_labels = None
depends_on = None


def upgrade():
    """No-op upgrade to satisfy migration chain."""
    pass


def downgrade():
    """No-op downgrade."""
    pass

