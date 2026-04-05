"""Add new fields to baby_configs table

Revision ID: 002_add_baby_config_fields
Revises: 001_initial
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_baby_config_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to baby_configs table
    op.add_column('baby_configs', sa.Column('gender', sa.String(16), nullable=True, server_default='unknown'))
    op.add_column('baby_configs', sa.Column('birth_weight', sa.Float(), nullable=True))
    op.add_column('baby_configs', sa.Column('feeding_type', sa.String(16), nullable=True, server_default='mixed'))


def downgrade() -> None:
    op.drop_column('baby_configs', 'feeding_type')
    op.drop_column('baby_configs', 'birth_weight')
    op.drop_column('baby_configs', 'gender')