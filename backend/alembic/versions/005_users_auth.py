"""add users table for authentication

Revision ID: 005
Revises: 004
Create Date: 2026-05-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("login", sa.String(120), nullable=False),
        sa.Column("password", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_login_lower ON users (LOWER(login))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_users_login_lower")
    op.drop_table("users")

