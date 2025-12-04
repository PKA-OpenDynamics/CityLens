"""merge_branches

Revision ID: 70c70e352761
Revises: 4c8f9e3d1a2b, 3a7f8e9c2d1b
Create Date: 2025-12-04 03:53:34.497751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70c70e352761'
down_revision: Union[str, None] = ('4c8f9e3d1a2b', '3a7f8e9c2d1b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

