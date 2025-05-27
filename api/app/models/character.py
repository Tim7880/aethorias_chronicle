# Path: api/app/models/character.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .campaign_member import CampaignMember
    from .character_skill import CharacterSkill # <--- ADD THIS IMPORT

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

    strength = Column(Integer, default=10, nullable=False)
    dexterity = Column(Integer, default=10, nullable=False)
    constitution = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    charisma = Column(Integer, default=10, nullable=False)

    hit_points_current = Column(Integer, nullable=True)
    hit_points_max = Column(Integer, nullable=True)
    armor_class = Column(Integer, nullable=True)

    inventory = Column(JSON, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="characters")

    campaign_participations = relationship(
        "CampaignMember", 
        back_populates="character",
        cascade="all, delete-orphan"
    )

    # Relationship to CharacterSkill association table
    skills = relationship(
        "CharacterSkill", 
        back_populates="character_owner", 
        cascade="all, delete-orphan" # If character is deleted, their skill associations are deleted
    ) # <--- ADD THIS RELATIONSHIP


