# Path: api/app/models/character_item.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character # For relationship type hinting
    from .item import Item # For relationship type hinting

class CharacterItem(Base):
    __tablename__ = "character_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    quantity = Column(Integer, default=1, nullable=False)
    is_equipped = Column(Boolean, default=False, nullable=False)
    # custom_description or notes for this specific instance of the item could be added here

    # Relationships
    character_owner = relationship("Character", back_populates="inventory_items")
    item_definition = relationship("Item", back_populates="character_associations")

    # A character should typically have one entry for a specific item type,
    # quantity handles multiples. If items can have unique instances (e.g. magical sword +1 vs another magical sword +1)
    # then this constraint might be removed or rethought. For now, one entry per item_id per character.
    __table_args__ = (UniqueConstraint('character_id', 'item_id', name='_character_item_uc'),)




    