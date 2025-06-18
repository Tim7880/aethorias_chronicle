"""add active turn tracking to campaign session

Revision ID: 253486e59afe
Revises: 2a8974fc9812
Create Date: 2025-06-18 12:26:04.523014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '253486e59afe'
down_revision: Union[str, None] = '2a8974fc9812'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### Manually Corrected Alembic Commands ###
    op.add_column('campaign_sessions', sa.Column('active_initiative_entry_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_campaign_sessions_active_initiative_entry_id', # Constraint name
        'campaign_sessions', 'initiative_entries',
        ['active_initiative_entry_id'], ['id'],
        use_alter=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### Manually Corrected Alembic Commands ###
    op.drop_constraint(
        'fk_campaign_sessions_active_initiative_entry_id',
        'campaign_sessions', 
        type_='foreignkey'
    )
    op.drop_column('campaign_sessions', 'active_initiative_entry_id')
    # ### end Alembic commands ###


