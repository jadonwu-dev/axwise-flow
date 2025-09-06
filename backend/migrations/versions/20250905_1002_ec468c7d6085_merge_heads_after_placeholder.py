"""merge heads after placeholder

Revision ID: ec468c7d6085
Revises: 20250813_1200, 5301c8fb020d
Create Date: 2025-09-05 10:02:03.293716+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec468c7d6085'
down_revision = ('20250813_1200', '5301c8fb020d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
