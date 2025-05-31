# Path: api/app/schemas/character_spell.py
from pydantic import BaseModel, Field
from typing import Optional

# Import the base Spell schema for nesting in responses
from .spell import Spell as SpellSchema # Assuming your Spell response schema is named Spell

class CharacterSpellBase(BaseModel):
    spell_id: int
    is_known: bool = False
    is_prepared: bool = False

class CharacterSpellCreate(CharacterSpellBase):
    # For Sorcerers learning spells/cantrips, we'll set these to True by default in CRUD
    is_known: bool = True 
    is_prepared: bool = True # Sorcerers "know" spells, which are effectively always "prepared"

class CharacterSpellUpdate(BaseModel): # For casters who prepare spells
    is_prepared: Optional[bool] = None
    # is_known might not be updatable directly here for most classes once learned

class CharacterSpell(CharacterSpellBase): # For API responses
    id: int
    # character_id: int # Usually known from the context of the parent Character schema
    spell_definition: SpellSchema # Nested full spell details

    class Config:
        from_attributes = True



        