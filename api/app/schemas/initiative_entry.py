# Path: api/app/schemas/initiative_entry.py
from pydantic import BaseModel, field_validator
from typing import Optional

class InitiativeEntryBase(BaseModel):
    initiative_roll: int
    character_id: Optional[int] = None
    monster_name: Optional[str] = None

    @field_validator('monster_name')
    def character_or_monster(cls, v, values):
        if 'character_id' in values.data and values.data['character_id'] is not None and v is not None:
            raise ValueError('Cannot provide both character_id and monster_name')
        if 'character_id' not in values.data and v is None:
            raise ValueError('Must provide either character_id or monster_name')
        return v

class InitiativeEntryCreate(InitiativeEntryBase):
    pass

class InitiativeEntry(InitiativeEntryBase):
    id: int
    session_id: int

    class Config:
        from_attributes = True
