# Path: api/app/models/item.py
from sqlalchemy import Column, Integer, String, Text, Float, Enum as SQLAlchemyEnum, JSON # <--- ADD JSON HERE
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from typing import TYPE_CHECKING
import enum # For Python enums

if TYPE_CHECKING:
    from .character_item import CharacterItem # For relationship type hinting

# Python Enum for ItemType
class ItemTypeEnum(enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    ADVENTURING_GEAR = "adventuring_gear"
    TOOL = "tool"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    RING = "ring"
    WONDROUS_ITEM = "wondrous_item"
    CURRENCY = "currency"
    OTHER = "other"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    item_type = Column(SQLAlchemyEnum(ItemTypeEnum, name="itemtypeenum"), nullable=False, default=ItemTypeEnum.OTHER)
    
    weight = Column(Float, nullable=True, default=0.0) 
    cost_gp = Column(Float, nullable=True, default=0.0) 

    properties = Column(JSON, nullable=True) # JSON type is now imported

    character_associations = relationship("CharacterItem", back_populates="item_definition")



