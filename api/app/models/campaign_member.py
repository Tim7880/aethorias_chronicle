# Path: api/app/models/campaign_member.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User # For type hinting
    from .campaign import Campaign # For type hinting
    from .character import Character # For type hinting

class CampaignMember(Base):
    __tablename__ = "campaign_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Simple PK

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # The user who is a player
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True) # Character used by the player in this campaign

    # role = Column(String(50), default="Player", nullable=False) # Future: could add roles like "Co-DM"

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Define relationships
    campaign = relationship("Campaign", back_populates="members")
    user = relationship("User", back_populates="campaign_memberships")
    character = relationship("Character", back_populates="campaign_participations")

    # Ensure a user can only join a campaign once (with one or no character initially)
    # A user could potentially have multiple characters in the same campaign if we remove this constraint
    # or handle it differently, but for MVP, one character per user per campaign is simpler.
    # If character_id can be NULL, this constraint might need adjustment or be handled at app level.
    # For now, let's assume a user is just a member, character assignment can be flexible.
    # A better constraint might be just (campaign_id, user_id) is unique.
    __table_args__ = (UniqueConstraint('campaign_id', 'user_id', name='_campaign_user_uc'),)


    