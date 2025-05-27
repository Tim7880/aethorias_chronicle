# Path: api/app/models/character_spell.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character  # For relationship type hinting
    from .spell import Spell          # For relationship type hinting

class CharacterSpell(Base):
    __tablename__ = "character_spells"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    spell_id = Column(Integer, ForeignKey("spells.id"), nullable=False, index=True)

    # Additional attributes for the association
    is_known = Column(Boolean, default=True, nullable=False)
    # 'is_prepared' is relevant for classes like Wizards, Clerics, Druids, Paladins.
    # For Sorcerers, Bards, Warlocks, Rangers (who know spells directly), this might always be False or not applicable.
    # Defaulting to False seems reasonable for an MVP.
    is_prepared = Column(Boolean, default=False, nullable=False) 

    # Relationships
    character_owner = relationship("Character", back_populates="known_spells") # UPDATED back_populates
    spell_definition = relationship("Spell", back_populates="character_associations")

    # A character should typically have only one entry for a specific spell_id.
    __table_args__ = (UniqueConstraint('character_id', 'spell_id', name='_character_spell_uc'),)



    