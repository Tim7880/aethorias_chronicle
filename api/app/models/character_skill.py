# Path: api/app/models/character_skill.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression # For server_default with Boolean
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character
    from .skill import Skill

class CharacterSkill(Base):
    __tablename__ = "character_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    is_proficient = Column(Boolean, default=False, nullable=False)
    has_expertise = Column(Boolean, default=False, nullable=False, server_default=expression.false()) # <--- NEW FIELD

    character_owner = relationship("Character", back_populates="skills")
    skill_definition = relationship("Skill", back_populates="character_skill_associations")

    __table_args__ = (UniqueConstraint('character_id', 'skill_id', name='_character_skill_uc'),)