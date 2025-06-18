# Path: api/app/models/campaign_session.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
import sqlalchemy as sa

from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .campaign import Campaign
    from .initiative_entry import InitiativeEntry

class CampaignSession(Base):
    __tablename__ = "campaign_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # This JSON field will store flexible data like the current map URL,
    # token positions, fog of war data, etc.
    map_state = Column(JSON, nullable=True, server_default=sa.text("'{}'::jsonb"))

    # Relationships
    campaign = relationship("Campaign", back_populates="sessions")
    initiative_entries = relationship("InitiativeEntry", back_populates="session", cascade="all, delete-orphan")
    

