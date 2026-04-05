"""Initial database migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('openid', sa.String(64), unique=True, nullable=False),
        sa.Column('nickname', sa.String(128), nullable=True),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_openid', 'users', ['openid'])

    # Create baby_configs table
    op.create_table(
        'baby_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('baby_name', sa.String(64), nullable=True, default='宝宝'),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create records table
    op.create_table(
        'records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(32), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('images', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_records_user_id', 'records', ['user_id'])
    op.create_index('ix_records_type', 'records', ['type'])
    op.create_index('ix_records_timestamp', 'records', ['timestamp'])
    op.create_index('ix_records_date', 'records', ['date'])
    # Composite index for common query pattern
    op.create_index('ix_records_user_date', 'records', ['user_id', 'date'])


def downgrade() -> None:
    op.drop_table('records')
    op.drop_table('baby_configs')
    op.drop_table('users')