"""add_attendance_status_column

Revision ID: 7f3c2b1a9e11
Revises: d246ea078da7
Create Date: 2026-03-18 20:25:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f3c2b1a9e11"
down_revision: Union[str, None] = "d246ea078da7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("attendance_records", sa.Column("attendance_status", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("attendance_records", "attendance_status")

