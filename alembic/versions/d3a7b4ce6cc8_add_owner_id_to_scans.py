"""add owner_id to scans

Revision ID: d3a7b4ce6cc8
Revises: 29496af70a73
Create Date: 2026-06-24 11:08:10.068595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3a7b4ce6cc8'
down_revision: Union[str, Sequence[str], None] = '29496af70a73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('scans', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_scans_owner_id_users', 'scans', 'users', ['owner_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_scans_owner_id_users', 'scans', type_='foreignkey')
    op.drop_column('scans', 'owner_id')
