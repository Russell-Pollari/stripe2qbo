"""Not null qbo

Revision ID: 1e41b1c1a118
Revises: ca3daa85815f
Create Date: 2023-10-01 19:56:21.315058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1e41b1c1a118"
down_revision: Union[str, None] = "ca3daa85815f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("qbo_realm_id", existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "qbo_realm_id", existing_type=sa.VARCHAR(), nullable=False
        )
