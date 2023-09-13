"""Init

Revision ID: b4ab3a7e9e14
Revises:
Create Date: 2023-09-12 20:16:19.665538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4ab3a7e9e14"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("qbo_realm_id", sa.String(), nullable=False),
        sa.Column("stripe_clearing_account_id", sa.String(), nullable=False),
        sa.Column("stripe_payout_account_id", sa.String(), nullable=False),
        sa.Column("stripe_vendor_id", sa.String(), nullable=False),
        sa.Column("stripe_fee_account_id", sa.String(), nullable=False),
        sa.Column("default_income_account_id", sa.String(), nullable=False),
        sa.Column("default_tax_code_id", sa.String(), nullable=False),
        sa.Column("exempt_tax_code_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qbo_realm_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("qbo_realm_id", sa.String(), nullable=False),
        sa.Column("stripe_user_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qbo_realm_id"),
    )
    op.create_table(
        "qbo_tokens",
        sa.Column("realm_id", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.String(), nullable=False),
        sa.Column("refresh_token_expires_at", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("realm_id"),
    )
    op.create_table(
        "transaction_sync",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("fee", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("stripe_id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "success", "failed", native_enum=False),
            nullable=False,
        ),
        sa.Column("transfer_id", sa.String(), nullable=True),
        sa.Column("invoice_id", sa.String(), nullable=True),
        sa.Column("payment_id", sa.String(), nullable=True),
        sa.Column("expense_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transaction_sync")
    op.drop_table("qbo_tokens")
    op.drop_table("users")
    op.drop_table("sync_settings")
