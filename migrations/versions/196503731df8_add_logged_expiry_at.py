depends_on = None
"""Add logged_expiry_at column (already present in updated baseline) and ensure supporting indexes.

This migration was originally creating several indexes that are now part of the
baseline migration. To avoid duplicate-index errors on fresh databases we make
the upgrade idempotent: only add the column if missing and skip index creation.

Revision ID: 196503731df8
Revises: 368261dcbc49
Create Date: 2025-10-22 16:30:01.280481
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '196503731df8'
down_revision = '368261dcbc49'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'insurance_policy' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('insurance_policy')]
        if 'logged_expiry_at' not in cols:
            op.add_column('insurance_policy', sa.Column('logged_expiry_at', sa.DateTime(), nullable=True))
    # Indexes already exist in baseline; skip re-creation.


def downgrade():
    # Downgrade only removes the column if it was added here.
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'insurance_policy' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('insurance_policy')]
        if 'logged_expiry_at' in cols:
            op.drop_column('insurance_policy', 'logged_expiry_at')
