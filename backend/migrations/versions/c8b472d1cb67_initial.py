"""initial

Revision ID: c8b472d1cb67
Revises: 51e574a947f9
Create Date: 2026-06-07 22:39:40.875532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8b472d1cb67'
down_revision: Union[str, Sequence[str], None] = '51e574a947f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
