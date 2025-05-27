# Path: api/app/schemas/item.py
from pydantic import BaseModel, Field
from typing import Optional, Any # Any for the JSON 'properties' field
from app.models.item import ItemTypeEnum # Import the Enum from your Item model

# --- Item Schemas (for the predefined list of D&D items) ---

class ItemBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    item_type: ItemTypeEnum = ItemTypeEnum.OTHER
    weight: Optional[float] = 0.0
    cost_gp: Optional[float] = 0.0
    properties: Optional[Any] = None # For flexible item-specific attributes (e.g., damage for weapons)

class ItemCreate(ItemBase): # For initially populating the items table (seeding)
    pass

class ItemUpdate(ItemBase): # Unlikely to be used by users for SRD items, more for admin/homebrew
    name: Optional[str] = Field(None, max_length=100)
    item_type: Optional[ItemTypeEnum] = None
    # All fields are optional for update

class Item(ItemBase): # For API responses when listing available items or nested in CharacterItem
    id: int

    class Config:
        from_attributes = True

# --- CharacterItem Schemas (linking Characters to Items with quantity, equipped status) ---

class CharacterItemBase(BaseModel):
    item_id: int # The ID of the item from the 'items' table
    quantity: int = Field(1, ge=1) # Quantity must be at least 1
    is_equipped: bool = False

class CharacterItemCreate(CharacterItemBase): # When adding an item to a character's inventory
    pass

class CharacterItemUpdate(BaseModel): # For updating quantity or equipped status
    quantity: Optional[int] = Field(None, ge=1)
    is_equipped: Optional[bool] = None

class CharacterItem(CharacterItemBase): # For API responses showing an item in a character's inventory
    id: int # ID of the CharacterItem association entry
    # character_id: int # Usually known from context (e.g., fetched as part of a character's inventory)
    item_definition: Item # Nested Item schema to show full item details

    class Config:
        from_attributes = True


        