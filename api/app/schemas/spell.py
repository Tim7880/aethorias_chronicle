# Path: api/app/schemas/spell.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any # Any for dnd_classes JSON
from app.models.spell import SchoolOfMagicEnum # Import the Enum from your Spell model

class SpellBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    higher_level: Optional[str] = None
    range: str = Field(..., max_length=100)
    components: str = Field(..., max_length=255) # e.g., "V, S, M"
    material: Optional[str] = None
    ritual: bool = False
    duration: str = Field(..., max_length=100)
    concentration: bool = False
    casting_time: str = Field(..., max_length=100)
    level: int = Field(..., ge=0, le=9) # Cantrips are level 0
    school: SchoolOfMagicEnum
    dnd_classes: Optional[List[str]] = [] # Expect a list of class names for simplicity
    source_book: Optional[str] = Field("SRD", max_length=100)

class SpellCreate(SpellBase): # For initially populating the spells table (seeding)
    pass

# Update schema might not be directly exposed to users for SRD spells
class SpellUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    higher_level: Optional[str] = None
    range: Optional[str] = Field(None, max_length=100)
    components: Optional[str] = Field(None, max_length=255)
    material: Optional[str] = None
    ritual: Optional[bool] = None
    duration: Optional[str] = Field(None, max_length=100)
    concentration: Optional[bool] = None
    casting_time: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=0, le=9)
    school: Optional[SchoolOfMagicEnum] = None
    dnd_classes: Optional[List[str]] = None
    source_book: Optional[str] = Field(None, max_length=100)

class Spell(SpellBase): # For API responses when listing available spells
    id: int

    class Config:
        from_attributes = True



        