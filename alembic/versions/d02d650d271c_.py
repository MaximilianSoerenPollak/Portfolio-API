"""empty message

Revision ID: d02d650d271c
Revises: c56c102dee63
Create Date: 2022-03-08 16:37:09.920003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d02d650d271c"
down_revision = "c56c102dee63"
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column("stocks",
    # sa.Column("yahoo_ticker", sa.String(), nullable=False),
    # sa.Column("exchange", sa.String(), nullable=True),
    # sa.Column("sector", sa.String(), nullable=True),
    # sa.Column("industry", sa.String(), nullable=True),
    # sa.Column("long_business_summary", sa.Text(), nullable=True),
    # sa.Column("country", sa.String(), nullable=True),
    # sa.Column("website", sa.String(), nullable=True),
    # sa.Column("price", sa.Float(), nullable=False),
    # sa.Column("marketcap", sa.Integer(), nullable=True),
    # sa.Column("dividends", sa.Float(), nullable=True),
    # sa.Column("dividend_yield", sa.Float(), nullable=True),
    # sa.Column("ex_dividend_date", sa.Date(), nullable=True),
    # sa.Column("beta", sa.Float(), nullable=True),
    # sa.Column("fifty_two_week_high", sa.Float(), nullable=True),
    # sa.Column("fifty_two_week_low", sa.Float(), nullable=True),
    # sa.Column("fifty_day_avg", sa.Float(), nullable=True),
    # sa.Column("recommendation", sa.String(), nullable=True),
    # sa.Column("total_cash_per_share", sa.Float(), nullable=True),
    # sa.Column("profit_margins", sa.Float(), nullable=True),
    # sa.Column("status", sa.Integer(), nullable=False, server_default="0"),
    # sa.Column("created_by", sa.Integer(), nullable=True),
    # sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("NOW()")),
    # sa.Column("updated_at", sa.TIMESTAMP(), nullable=True, onupdate=sa.text("NOW()")),
    # sa.Column("portfolios", sa.Relationship()))
    pass


def downgrade():
    pass
