"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(18)),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "controls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module", sa.String(20), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("catalog_version", sa.String(20), nullable=False),
        sa.Column("guidance_ref", sa.String(100)),
        sa.UniqueConstraint("module", "code", name="uq_control_module_code"),
    )
    op.create_index("ix_controls_module", "controls", ["module"])
    op.create_table(
        "audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("module", sa.String(20), nullable=False),
        sa.Column("audit_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20)),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("ix_audits_module", "audits", ["module"])
    op.create_table(
        "audit_responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_id", sa.Integer(), sa.ForeignKey("audits.id"), nullable=False),
        sa.Column("control_id", sa.Integer(), sa.ForeignKey("controls.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("work_in_progress", sa.Boolean()),
        sa.Column("notes", sa.Text()),
        sa.UniqueConstraint("audit_id", "control_id", name="uq_audit_control"),
    )


def downgrade() -> None:
    op.drop_table("audit_responses")
    op.drop_table("audits")
    op.drop_table("controls")
    op.drop_table("companies")
