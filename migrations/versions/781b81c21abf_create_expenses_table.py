"""create expenses table

Revision ID: 781b81c21abf
Revises:
Create Date: 2026-09-03 13:12:43.569077

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '781b81c21abf'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expenses",
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "amount >= 0",
            name="expenses_amount_check",
        ),
        sa.PrimaryKeyConstraint(
            "expense_id",
            name="expenses_pkey",
        ),
    )


def downgrade() -> None:
    op.drop_table("expenses")
