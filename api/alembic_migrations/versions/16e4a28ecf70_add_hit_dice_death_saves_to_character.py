"""add_hit_dice_death_saves_to_character

Revision ID: 16e4a28ecf70
Revises: 3dfac716a13d
Create Date: 2025-05-29 17:11:43.044253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16e4a28ecf70'
down_revision: Union[str, None] = '3dfac716a13d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('characters', sa.Column('hit_dice_total', sa.Integer(), server_default=sa.text('1'), nullable=False))
    op.add_column('characters', sa.Column('hit_dice_remaining', sa.Integer(), server_default=sa.text('1'), nullable=False))
    op.add_column('characters', sa.Column('death_save_successes', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('characters', sa.Column('death_save_failures', sa.Integer(), server_default=sa.text('0'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('characters', 'death_save_failures')
    op.drop_column('characters', 'death_save_successes')
    op.drop_column('characters', 'hit_dice_remaining')
    op.drop_column('characters', 'hit_dice_total')
    # ### end Alembic commands ###
