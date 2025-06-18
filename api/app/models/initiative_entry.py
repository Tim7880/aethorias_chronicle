# Path: api/app/models/initiative_entry.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .campaign_session import CampaignSession
    from .character import Character

class InitiativeEntry(Base):
    __tablename__ = "initiative_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    session_id = Column(Integer, ForeignKey("campaign_sessions.id"), nullable=False, index=True)
    
    # An entry can be a player character OR a manually added monster/NPC
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True) 
    monster_name = Column(String(100), nullable=True) # For manually added combatants
    
    initiative_roll = Column(Integer, nullable=False, index=True)

    # Relationships
    session = relationship("CampaignSession", back_populates="initiative_entries")
    character = relationship("Character")

