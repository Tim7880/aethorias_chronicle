# Path: api/app/models/spell.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLAlchemyEnum, JSON
from sqlalchemy.orm import relationship # <--- Ensure relationship is imported
from app.db.base_class import Base
import enum 
from typing import TYPE_CHECKING # <--- ADD THIS IMPORT

if TYPE_CHECKING: # <--- ADD THIS BLOCK
    from .character_spell import CharacterSpell # For relationship type hinting

class SchoolOfMagicEnum(enum.Enum):
    ABJURATION = "Abjuration"
    CONJURATION = "Conjuration"
    DIVINATION = "Divination"
    ENCHANTMENT = "Enchantment"
    EVOCATION = "Evocation"
    ILLUSION = "Illusion"
    NECROMANCY = "Necromancy"
    TRANSMUTATION = "Transmutation"
    UNIVERSAL = "Universal"

class Spell(Base):
    __tablename__ = "spells"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    higher_level = Column(Text, nullable=True)

    range = Column(String(100), nullable=False)
    components = Column(String(255), nullable=False)
    material = Column(Text, nullable=True)

    ritual = Column(Boolean, default=False, nullable=False)
    duration = Column(String(100), nullable=False)
    concentration = Column(Boolean, default=False, nullable=False)
    casting_time = Column(String(100), nullable=False)

    level = Column(Integer, nullable=False, index=True)
    school = Column(SQLAlchemyEnum(SchoolOfMagicEnum, name="schoolofmagicenum"), nullable=False)
    
    dnd_classes = Column(JSON, nullable=True) 
    source_book = Column(String(100), nullable=True, default="SRD")

    # --- NEW RELATIONSHIP TO CharacterSpell ---
    character_associations = relationship(
        "CharacterSpell", 
        back_populates="spell_definition"
    ) # <--- ADD THIS RELATIONSHIP
    # --- END NEW RELATIONSHIP ---



    