"""Add research sessions tables

Revision ID: add_research_sessions
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_research_sessions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create research_sessions table
    op.create_table('research_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('business_idea', sa.Text(), nullable=True),
        sa.Column('target_customer', sa.Text(), nullable=True),
        sa.Column('problem', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('stage', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('messages', sa.JSON(), nullable=True),
        sa.Column('conversation_context', sa.Text(), nullable=True),
        sa.Column('questions_generated', sa.Boolean(), nullable=True),
        sa.Column('research_questions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_sessions_id'), 'research_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_research_sessions_user_id'), 'research_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_research_sessions_session_id'), 'research_sessions', ['session_id'], unique=True)

    # Create research_exports table
    op.create_table('research_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('export_type', sa.String(), nullable=True),
        sa.Column('export_format', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['research_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('research_exports')
    op.drop_index(op.f('ix_research_sessions_session_id'), table_name='research_sessions')
    op.drop_index(op.f('ix_research_sessions_user_id'), table_name='research_sessions')
    op.drop_index(op.f('ix_research_sessions_id'), table_name='research_sessions')
    op.drop_table('research_sessions')
