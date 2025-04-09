"""add archetype column to personas table

Revision ID: 20250408_1200
Revises: 20250407_1125
Create Date: 2025-04-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250408_1200'
down_revision = '20250407_1125'
branch_labels = None
depends_on = None

def upgrade():
    # Add archetype column to personas table
    op.add_column('personas', sa.Column('archetype', sa.String(), nullable=True))
    
    # Add other missing columns from the Persona model
    op.add_column('personas', sa.Column('demographics', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('goals_and_motivations', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('skills_and_expertise', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('workflow_and_environment', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('challenges_and_frustrations', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('needs_and_desires', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('technology_and_tools', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('attitude_towards_research', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('attitude_towards_ai', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('key_quotes', sa.JSON(), nullable=True))
    op.add_column('personas', sa.Column('overall_confidence', sa.Float(), nullable=True))
    op.add_column('personas', sa.Column('supporting_evidence_summary', sa.JSON(), nullable=True))

def downgrade():
    # Remove the added columns
    op.drop_column('personas', 'archetype')
    op.drop_column('personas', 'demographics')
    op.drop_column('personas', 'goals_and_motivations')
    op.drop_column('personas', 'skills_and_expertise')
    op.drop_column('personas', 'workflow_and_environment')
    op.drop_column('personas', 'challenges_and_frustrations')
    op.drop_column('personas', 'needs_and_desires')
    op.drop_column('personas', 'technology_and_tools')
    op.drop_column('personas', 'attitude_towards_research')
    op.drop_column('personas', 'attitude_towards_ai')
    op.drop_column('personas', 'key_quotes')
    op.drop_column('personas', 'overall_confidence')
    op.drop_column('personas', 'supporting_evidence_summary')
