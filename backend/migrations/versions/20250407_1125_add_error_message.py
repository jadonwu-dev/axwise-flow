"""add error_message column

Revision ID: 20250407_1125
Revises: 20250407_1115
Create Date: 2025-04-07 11:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250407_1125'
down_revision = '20250407_1115'
branch_labels = None
depends_on = None

def upgrade():
    # Add error_message column to analysis_results table
    op.add_column('analysis_results', sa.Column('error_message', sa.Text(), nullable=True))

def downgrade():
    # Remove the error_message column
    op.drop_column('analysis_results', 'error_message')
