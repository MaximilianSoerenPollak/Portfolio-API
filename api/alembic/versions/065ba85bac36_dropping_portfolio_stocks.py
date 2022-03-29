"""dropping portfolio_stocks

Revision ID: 065ba85bac36
Revises: a1587b0d4e81
Create Date: 2022-03-29 14:15:23.530861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "065ba85bac36"
down_revision = "ad1b0bfc6b53"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("portfolio_stocks")


def downgrade():
    pass
