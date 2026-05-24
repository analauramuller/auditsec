"""company unique constraints

Revision ID: 002
Revises: 001
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_name_lower ON companies (LOWER(name))"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_cnpj
        ON companies (cnpj) WHERE cnpj IS NOT NULL AND cnpj <> ''
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_companies_cnpj")
    op.execute("DROP INDEX IF EXISTS uq_companies_name_lower")
