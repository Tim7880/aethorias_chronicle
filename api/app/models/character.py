# Path: api/app/models/character.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON, Boolean
import sqlalchemy as sa 
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import expression # No longer needed if default is None for string
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # ... (your existing imports) ...
    from .user import User
    from .campaign_member import CampaignMember
    from .character_skill import CharacterSkill
    from .character_item import CharacterItem
    from .character_spell import CharacterSpell


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    # ... (other existing fields: user_id, race, character_class, level, experience_points, etc.) ...
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

    # --- MODIFIED FIELD for Leveling Status ---
    # Was: has_pending_level_up = Column(Boolean, default=False, nullable=False, server_default=expression.false())
    level_up_status = Column(String(50), nullable=True, default=None) # e.g., "pending_hp", "pending_asi", None
    # --- END MODIFIED FIELD ---

    # ... (relationships: inventory_items, skills, known_spells, owner, campaign_participations) ...
    inventory_items = relationship(
        "CharacterItem", back_populates="character_owner", cascade="all, delete-orphan"
    )
    skills = relationship(
        "CharacterSkill", back_populates="character_owner", cascade="all, delete-orphan"
    )
    known_spells = relationship(
        "CharacterSpell", back_populates="character_owner", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    owner = relationship("User", back_populates="characters")
    campaign_participations = relationship(
        "CampaignMember", back_populates="character", cascade="all, delete-orphan"
    )
