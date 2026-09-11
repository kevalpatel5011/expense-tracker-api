"""add expense query indexes

Revision ID: 8f542f49f332
Revises: 781b81c21abf
Create Date: 2026-09-11 12:38:49.602088

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8f542f49f332'
down_revision: str | Sequence[str] | None = '781b81c21abf'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_expenses_date",
        "expenses",
        ["date"],
        unique=False,
    )
    op.create_index(
        "ix_expenses_amount",
        "expenses",
        ["amount"],
        unique=False,
    )
    op.create_index(
        "ix_expenses_normalized_category",
        "expenses",
        [sa.text("LOWER(TRIM(category))")],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_expenses_normalized_category",
        table_name="expenses",
    )
    op.drop_index(
        "ix_expenses_amount",
        table_name="expenses",
    )
    op.drop_index(
        "ix_expenses_date",
        table_name="expenses",
    )
