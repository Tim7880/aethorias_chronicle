# Path: api/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app.db.base_class import Base
from typing import TYPE_CHECKING # <--- ADD THIS

if TYPE_CHECKING: # <--- ADD THIS BLOCK
    from .character import Character # For characters relationship
    from .campaign import Campaign # For campaigns_as_dm relationship
    from .campaign_member import CampaignMember # For campaign_memberships relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    preferred_timezone = Column(String, nullable=True, server_default='UTC')
    is_active = Column(Boolean(), server_default=expression.true(), nullable=False)
    is_superuser = Column(Boolean(), server_default=expression.false(), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to Character model
    characters = relationship(
        "Character", 
        back_populates="owner", 
        cascade="all, delete-orphan"
    ) 

    # Relationship to Campaigns where this user is the DM
    campaigns_as_dm = relationship(
        "Campaign", 
        back_populates="dm", 
        cascade="all, delete-orphan" # If DM user is deleted, their campaigns are deleted
    ) # <--- ADD THIS RELATIONSHIP

    # Relationship to CampaignMember (campaigns this user is a player in)
    campaign_memberships = relationship(
        "CampaignMember", 
        back_populates="user", 
        cascade="all, delete-orphan" # If user is deleted, their memberships are removed
    ) # <--- ADD THIS RELATIONSHIP