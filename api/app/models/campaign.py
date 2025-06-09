# Path: api/app/models/campaign.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING
import sqlalchemy as sa # Import sa for server_default text

if TYPE_CHECKING:
    from .user import User
    from .campaign_member import CampaignMember

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    dm_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    banner_image_url = Column(String(512), nullable=True)
    max_players = Column(Integer, nullable=True)
    next_session_utc = Column(DateTime(timezone=True), nullable=True)
    house_rules = Column(Text, nullable=True)

    # --- NEW FIELD for Session Notes ---
    session_notes = Column(Text, nullable=True)
    # --- END NEW FIELD ---

    is_open_for_recruitment = Column(Boolean, default=False, nullable=False, server_default=sa.text('false'))

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    dm = relationship("User", back_populates="campaigns_as_dm")
    members = relationship(
        "CampaignMember", 
        back_populates="campaign", 
        cascade="all, delete-orphan"
    )

    