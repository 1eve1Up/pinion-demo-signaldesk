"""add optional contact email phone company

Revision ID: c4d9e2a18f10
Revises: 57ce458f0f81
Create Date: 2026-03-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4d9e2a18f10"
down_revision: Union[str, None] = "57ce458f0f81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contacts",
        sa.Column("email", sa.String(length=320), nullable=True),
    )
    op.add_column(
        "contacts",
        sa.Column("phone", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "contacts",
        sa.Column("company", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("contacts", "company")
    op.drop_column("contacts", "phone")
    op.drop_column("contacts", "email")
