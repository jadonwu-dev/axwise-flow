"""merge conflicting heads

Revision ID: 5301c8fb020d
Revises: b2a69511d058, 20250814_1200_remove_persona_fields
Create Date: 2025-09-05 10:00:28.167832+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5301c8fb020d'
down_revision = ('b2a69511d058', '20250814_1200_remove_persona_fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
