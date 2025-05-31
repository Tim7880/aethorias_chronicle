# Path: api/app/models/character.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON, Boolean, Enum as SQLAlchemyEnum
import sqlalchemy as sa 
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app.db.base_class import Base
from typing import TYPE_CHECKING

# Import the new Enum for the model field
from app.game_data.rogue_data import RoguishArchetypeEnum # <--- NEW IMPORT

if TYPE_CHECKING:
    from .user import User
    from .campaign_member import CampaignMember
    from .character_skill import CharacterSkill
    from .character_item import CharacterItem
    from .character_spell import CharacterSpell

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    race = Column(String(50), nullable=True)
    character_class = Column(String(50), nullable=True)
    level = Column(Integer, default=1, nullable=False)
    experience_points = Column(Integer, default=0, nullable=True)
    alignment = Column(String(50), nullable=True)
    
    background_story = Column(Text, nullable=True)
    appearance_description = Column(Text, nullable=True)
    is_ascended_tier = Column(Boolean, default=False, nullable=False, server_default=sa.text('false'))
    
    strength = Column(Integer, default=10, nullable=False)
    dexterity = Column(Integer, default=10, nullable=False)
    constitution = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    charisma = Column(Integer, default=10, nullable=False)
    
    hit_points_current = Column(Integer, nullable=True)
    hit_points_max = Column(Integer, nullable=True)
    armor_class = Column(Integer, nullable=True)
    hit_die_type = Column(Integer, nullable=True)
    hit_dice_total = Column(Integer, default=1, nullable=False, server_default=sa.text('1'))
    hit_dice_remaining = Column(Integer, default=1, nullable=False, server_default=sa.text('1'))
    death_save_successes = Column(Integer, default=0, nullable=False, server_default=sa.text('0'))
    death_save_failures = Column(Integer, default=0, nullable=False, server_default=sa.text('0'))
    level_up_status = Column(String(50), nullable=True, default=None)
    
    # --- NEW FIELD for Roguish Archetype ---
    roguish_archetype = Column(SQLAlchemyEnum(RoguishArchetypeEnum, name="roguisharchetypeenum"), nullable=True)
    # --- END NEW FIELD ---
        
    inventory_items = relationship("CharacterItem", back_populates="character_owner", cascade="all, delete-orphan")
    skills = relationship("CharacterSkill", back_populates="character_owner", cascade="all, delete-orphan")
    known_spells = relationship("CharacterSpell", back_populates="character_owner", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="characters")
    campaign_participations = relationship("CampaignMember", back_populates="character", cascade="all, delete-orphan")


    