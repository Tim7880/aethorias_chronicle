# Path: api/app/models/campaign_member.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint, Enum as SQLAlchemyEnum # <--- ADD SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING
import enum # <--- ADD enum

if TYPE_CHECKING:
    from .user import User
    from .campaign import Campaign
    from .character import Character

# --- NEW ENUM for Campaign Member Status ---
class CampaignMemberStatusEnum(enum.Enum):
    PENDING_APPROVAL = "pending_approval" # Player requested to join
    ACTIVE = "active"                     # Player is an active member
    REJECTED = "rejected"                 # Player's request was rejected
    INVITED = "invited"                   # DM invited player, awaiting player acceptance
    # LEFT = "left"                       # Future: Player left the campaign
    # KICKED = "kicked"                     # Future: DM removed player

class CampaignMember(Base):
    __tablename__ = "campaign_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # The user who is a player
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)

    status = Column(SQLAlchemyEnum(CampaignMemberStatusEnum, name="campaignmemberstatusenum"), 
                    nullable=False, 
                    default=CampaignMemberStatusEnum.PENDING_APPROVAL) # <--- NEW FIELD, default for player requests

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) # This might now represent 'request_sent_at' or 'status_updated_at'

    campaign = relationship("Campaign", back_populates="members")
    user = relationship("User", back_populates="campaign_memberships")
    character = relationship("Character", back_populates="campaign_participations")

    __table_args__ = (UniqueConstraint('campaign_id', 'user_id', name='_campaign_user_uc'),)


    