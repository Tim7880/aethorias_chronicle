"""add_status_to_campaign_members

Revision ID: 14c9c08f63aa
Revises: 0005a73c2eed
Create Date: 2025-05-28 18:05:35.571211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # For explicitly managing the ENUM type

# Define the Enum type explicitly for creation and dropping
campaignmemberstatusenum_type = postgresql.ENUM(
    'PENDING_APPROVAL', 'ACTIVE', 'REJECTED', 'INVITED',
    # Add any future statuses like 'LEFT', 'KICKED' here if defined in your Python Enum
    name='campaignmemberstatusenum', 
    create_type=False # Set to False for just referencing the type object initially
)

# revision identifiers, used by Alembic.
revision: str = '14c9c08f63aa' # e.g., the one from your filename
down_revision: Union[str, None] = '0005a73c2eed' # e.g., e9c82ed44bb5
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - MANUALLY ADJUSTED ###

    # 1. Create the ENUM type if it doesn't exist
    campaignmemberstatusenum_type.create(op.get_bind(), checkfirst=True)

    # 2. Add the column with a server_default for existing rows
    op.add_column('campaign_members', 
                  sa.Column('status', 
                            campaignmemberstatusenum_type, # Use the defined ENUM type
                            nullable=False, 
                            server_default=sa.text("'PENDING_APPROVAL'"))) # Default for existing rows
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - MANUALLY ADJUSTED ###
    op.drop_column('campaign_members', 'status')

    # 2. Drop the ENUM type
    campaignmemberstatusenum_type.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
