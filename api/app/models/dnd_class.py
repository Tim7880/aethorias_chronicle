# Path: api/app/models/dnd_class.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character # if you want a back-relationship

class DndClass(Base):
    __tablename__ = "dnd_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    hit_die = Column(Integer, nullable=False)
    
    # This relationship will link to the level-specific data
    levels = relationship("ClassLevel", back_populates="dnd_class", cascade="all, delete-orphan")

class ClassLevel(Base):
    __tablename__ = "class_levels"

    id = Column(Integer, primary_key=True, index=True)
    dnd_class_id = Column(Integer, ForeignKey("dnd_classes.id"), nullable=False)
    level = Column(Integer, nullable=False)
    
    proficiency_bonus = Column(Integer, nullable=False)
    
    # Store complex data like features or spellcasting info as JSON
    features = Column(JSON) # e.g., [{"name": "Expertise", "desc": "..."}, {"name": "Sneak Attack", "desc": "..."}]
    spellcasting = Column(JSON) # e.g., {"cantrips_known": 4, "spells_known": 2, "spell_slots_level_1": 2}
    
    # Relationship back to the parent class
    dnd_class = relationship("DndClass", back_populates="levels")