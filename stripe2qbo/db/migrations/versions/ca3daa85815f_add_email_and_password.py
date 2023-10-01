"""Add email and password

Revision ID: ca3daa85815f
Revises: 1ed1b82dc300
Create Date: 2023-09-30 09:23:50.144895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from stripe2qbo.api.auth import get_password_hash

# revision identifiers, used by Alembic.
revision: str = "ca3daa85815f"
down_revision: Union[str, None] = "1ed1b82dc300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "hashed_password",
                sa.String(),
                nullable=True,
            )
        )

    # Set email to qbo_realm_id and password to "password"
    # Obviously, wonky, but this will be run in prod before any users are created
    # This is just a way to migrate test data to the new schema
    op.execute("UPDATE users SET email = qbo_realm_id || '@test.com'")
    password = get_password_hash("password")
    op.execute(f"UPDATE users SET hashed_password = '{password}'")

    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_email", ["email"])
        batch_op.alter_column("email", nullable=False)
        batch_op.alter_column("hashed_password", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_email", "unique")
        batch_op.drop_column("hashed_password")
        batch_op.drop_column("email")
