"""add user_id to companies for per-user access control

Revision ID: 006
Revises: 005
Create Date: 2026-06-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_companies_user_id", "companies", ["user_id"])
    op.execute(
        """
        UPDATE companies
        SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1)
        WHERE user_id IS NULL
          AND EXISTS (SELECT 1 FROM users)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_companies_user_id", table_name="companies")
    op.drop_column("companies", "user_id")
