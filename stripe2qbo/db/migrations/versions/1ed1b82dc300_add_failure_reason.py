"""Add failure reason

Revision ID: 1ed1b82dc300
Revises: b4ab3a7e9e14
Create Date: 2023-09-28 12:37:16.594218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1ed1b82dc300"
down_revision: Union[str, None] = "b4ab3a7e9e14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transaction_sync", sa.Column("failure_reason", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("transaction_sync", "failure_reason")
