"""add optional note interaction_type and occurred_at

Revision ID: e7f8a9b0c1d2
Revises: c4d9e2a18f10
Create Date: 2026-03-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "c4d9e2a18f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notes",
        sa.Column("interaction_type", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "notes",
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notes", "occurred_at")
    op.drop_column("notes", "interaction_type")
