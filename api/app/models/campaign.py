# Path: api/app/models/campaign.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # For type hinting relationship
    from .campaign_member import CampaignMember # For type hinting relationship

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    dm_user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # The DM who owns/runs the campaign

    # Fields we discussed for DM campaign setup
    banner_image_url = Column(String(512), nullable=True)
    max_players = Column(Integer, nullable=True)
    next_session_utc = Column(DateTime(timezone=True), nullable=True)
    house_rules = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to the User who is the DM
    dm = relationship("User", back_populates="campaigns_as_dm")

    # Relationship to CampaignMember (one campaign can have many members/players)
    members = relationship(
        "CampaignMember", 
        back_populates="campaign", 
        cascade="all, delete-orphan"
    )



    