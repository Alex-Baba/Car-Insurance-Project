"""add logged_expiry_at

Revision ID: 196503731df8
Revises: 368261dcbc49
Create Date: 2025-10-22 16:30:01.280481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '196503731df8'
down_revision = '368261dcbc49'
branch_labels = None
depends_on = None


def upgrade():
    # Safely create if absent
    op.create_index("ix_car_vin", "car", ["vin"], unique=True)
    op.create_index("ix_policy_car_start_end", "insurance_policy", ["car_id","start_date","end_date"])
    op.create_index("ix_policy_car_end", "insurance_policy", ["car_id","end_date"])
    op.create_index("ix_claim_car_claim_date", "claim", ["car_id","claim_date"])


def downgrade():
    op.drop_index("ix_claim_car_claim_date", table_name="claim")
    op.drop_index("ix_policy_car_end", table_name="insurance_policy")
    op.drop_index("ix_policy_car_start_end", table_name="insurance_policy")
    op.drop_index("ix_car_vin", table_name="car")
