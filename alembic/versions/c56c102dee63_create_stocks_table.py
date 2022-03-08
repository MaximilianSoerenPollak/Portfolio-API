"""create stocks table

Revision ID: c56c102dee63
Revises: 
Create Date: 2022-03-08 16:26:02.766778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c56c102dee63"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
    )
    pass


def downgrade():
    op.drop_table("stocks")
    pass
