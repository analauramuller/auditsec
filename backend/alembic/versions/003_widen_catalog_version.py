"""widen catalog_version column

Revision ID: 003
Revises: 002
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "controls",
        "catalog_version",
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=False,
    )
    op.alter_column(
        "controls",
        "guidance_ref",
        existing_type=sa.String(100),
        type_=sa.String(120),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "controls",
        "guidance_ref",
        existing_type=sa.String(120),
        type_=sa.String(100),
        existing_nullable=True,
    )
    op.alter_column(
        "controls",
        "catalog_version",
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=False,
    )
