"""Add review fields to Analysis

Revision ID: ea8a48de3896
Revises: ff30f165d1b1
Create Date: 2026-08-08 23:32:43.636270

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea8a48de3896"
down_revision: str | Sequence[str] | None = "ff30f165d1b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("analyses", schema=None) as batch_op:
        batch_op.add_column(sa.Column("review_status", sa.String(), nullable=False, server_default="PENDING"))
        batch_op.add_column(sa.Column("reviewer_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("reviewer_notes", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index(batch_op.f("ix_analyses_reviewer_id"), ["reviewer_id"], unique=False)
        batch_op.create_foreign_key("fk_analyses_reviewer_id_users", "users", ["reviewer_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("analyses", schema=None) as batch_op:
        batch_op.drop_constraint("fk_analyses_reviewer_id_users", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_analyses_reviewer_id"))
        batch_op.drop_column("reviewed_at")
        batch_op.drop_column("reviewer_notes")
        batch_op.drop_column("reviewer_id")
        batch_op.drop_column("review_status")
    # ### end Alembic commands ###
