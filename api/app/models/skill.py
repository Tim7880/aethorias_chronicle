# Path: api/app/models/skill.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character_skill import CharacterSkill # For relationship type hinting

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True) # e.g., "Acrobatics", "Arcana"
    ability_modifier_name = Column(String(3), nullable=False) # e.g., "DEX", "INT", "WIS"
    description = Column(String(255), nullable=True) # Optional short description

    # Relationship to the CharacterSkill association table
    character_skill_associations = relationship("CharacterSkill", back_populates="skill_definition")