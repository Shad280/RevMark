"""
Add offer columns to message table

Revision ID: add_offer_columns_to_message
Revises: 
Create Date: 2025-10-17
"""
# revision identifiers, used by Alembic.
revision = '20251017_add_offer_columns_to_message'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('message', sa.Column('is_offer', sa.Boolean(), nullable=True))
    op.add_column('message', sa.Column('offer_approved', sa.Boolean(), nullable=True))
    op.add_column('message', sa.Column('offer_rejected', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('message', 'is_offer')
    op.drop_column('message', 'offer_approved')
    op.drop_column('message', 'offer_rejected')
