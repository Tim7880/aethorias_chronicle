# Path: api/app/schemas/character_spell.py
from pydantic import BaseModel, Field
from typing import Optional

from .spell import Spell as SpellSchema # To nest spell details in the response

class CharacterSpellBase(BaseModel):
    spell_id: int
    is_known: bool = True
    is_prepared: bool = False

class CharacterSpellCreate(CharacterSpellBase):
    # When creating, we just need the spell_id.
    # is_known and is_prepared will use defaults or can be set.
    pass

class CharacterSpellUpdate(BaseModel):
    # Only allow updating 'is_prepared' for now. 'is_known' is typically true if associated.
    # 'spell_id' and 'character_id' should not be updatable on an existing association.
    is_prepared: Optional[bool] = None

class CharacterSpell(CharacterSpellBase): # For API responses
    id: int # The ID of the CharacterSpell association record itself
    # character_id: int # Often known from context (e.g., part of a character's details)
    spell_definition: SpellSchema # Nested full spell details

    class Config:
        from_attributes = True



        