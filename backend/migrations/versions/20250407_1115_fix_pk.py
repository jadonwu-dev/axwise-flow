"""rename interview data primary key

Revision ID: 20250407_1115
Revises: add_analysis_result_status
Create Date: 2025-04-07 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250407_1115'
down_revision = 'add_analysis_result_status'
branch_labels = None
depends_on = None

def upgrade():
    # Rename the primary key column in interview_data table
    op.alter_column('interview_data', 'data_id', new_column_name='id')
    
    # Update the foreign key in analysis_results table
    op.drop_constraint('analysis_results_data_id_fkey', 'analysis_results', type_='foreignkey')
    op.create_foreign_key('analysis_results_data_id_fkey', 'analysis_results', 'interview_data', ['data_id'], ['id'])

def downgrade():
    # Revert the foreign key change
    op.drop_constraint('analysis_results_data_id_fkey', 'analysis_results', type_='foreignkey')
    op.create_foreign_key('analysis_results_data_id_fkey', 'analysis_results', 'interview_data', ['data_id'], ['data_id'])
    
    # Rename the column back
    op.alter_column('interview_data', 'id', new_column_name='data_id')
