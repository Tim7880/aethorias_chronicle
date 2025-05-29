# Path: api/app/schemas/character.py
from pydantic import BaseModel, Field, model_validator, ConfigDict # <--- ADD ConfigDict for Pydantic V2
from typing import Optional, List, Any 
from datetime import datetime

from .skill import CharacterSkill as CharacterSkillSchema
from .item import CharacterItem as CharacterItemSchema
from .character_spell import CharacterSpell as CharacterSpellSchema

# ... (CharacterBase remains the same, with level and XP) ...
class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    is_ascended_tier: bool = False
    level: Optional[int] = Field(1, ge=1) 
    experience_points: Optional[int] = Field(0, ge=0)
    alignment: Optional[str] = Field(None, max_length=50)
    background_story: Optional[str] = None
    appearance_description: Optional[str] = None
    strength: Optional[int] = Field(10, ge=1) 
    dexterity: Optional[int] = Field(10, ge=1)
    constitution: Optional[int] = Field(10, ge=1)
    intelligence: Optional[int] = Field(10, ge=1)
    wisdom: Optional[int] = Field(10, ge=1)
    charisma: Optional[int] = Field(10, ge=1)
    hit_points_current: Optional[int] = None
    hit_points_max: Optional[int] = Field(None, ge=1) 
    armor_class: Optional[int] = Field(None) 
    # inventory field was correctly removed here

    @model_validator(mode='after')
    def check_stats_based_on_tier(cls, data):
        # ... (your existing validator logic)
        if data is None: return data
        is_ascended = data.is_ascended_tier
        max_level = 50 if is_ascended else 30
        max_stat_value = 50 if is_ascended else 30
        max_ac_allowed = 80 if is_ascended else 40 
        max_hp_allowed = 2500 if is_ascended else 700
        if data.level is not None and not (1 <= data.level <= max_level):
            raise ValueError(f"Level ({data.level}) must be between 1 and {max_level} for this tier.")
        stats_to_check = [
            ("Strength", data.strength), ("Dexterity", data.dexterity), 
            ("Constitution", data.constitution), ("Intelligence", data.intelligence),
            ("Wisdom", data.wisdom), ("Charisma", data.charisma)
        ]
        for name, value in stats_to_check:
            if value is not None and not (1 <= value <= max_stat_value):
                raise ValueError(f"{name} ({value}) must be between 1 and {max_stat_value} for this tier.")
        if data.armor_class is not None and data.armor_class > max_ac_allowed:
            raise ValueError(f"Armor Class ({data.armor_class}) cannot exceed {max_ac_allowed} for this tier.")
        if data.hit_points_max is not None and data.hit_points_max > max_hp_allowed:
            raise ValueError(f"Max Hit Points ({data.hit_points_max}) cannot exceed {max_hp_allowed} for this tier.")
        return data

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel): 
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    is_ascended_tier: Optional[bool] = None
    # Level and XP are NOT here
    alignment: Optional[str] = Field(None, max_length=50)
    background_story: Optional[str] = None
    appearance_description: Optional[str] = None
    strength: Optional[int] = Field(None, ge=1)
    dexterity: Optional[int] = Field(None, ge=1)
    constitution: Optional[int] = Field(None, ge=1)
    intelligence: Optional[int] = Field(None, ge=1)
    wisdom: Optional[int] = Field(None, ge=1)
    charisma: Optional[int] = Field(None, ge=1)
    hit_points_current: Optional[int] = None
    hit_points_max: Optional[int] = Field(None, ge=1)
    armor_class: Optional[int] = Field(None)

    # --- ADD THIS CONFIGURATION FOR PYDANTIC V2 ---
    model_config = ConfigDict(extra='forbid')
    # --- OR FOR PYDANTIC V1 ---
    # class Config:
    #     extra = 'forbid' 
    # ---

    @model_validator(mode='after')
    def check_update_stats_based_on_tier(cls, data):
        # ... (your existing validator logic for CharacterUpdate - it should ideally not
        # re-validate things already handled by Field constraints if possible, 
        # or ensure it has enough context for tier-based validation if is_ascended_tier is updated)
        if data is None: return data
        if data.is_ascended_tier is not None: # Only apply tier-specific checks if tier is being touched
            effective_is_ascended = data.is_ascended_tier 
            max_stat_value = 50 if effective_is_ascended else 30
            max_ac_allowed = 80 if effective_is_ascended else 40 
            max_hp_allowed = 2500 if effective_is_ascended else 700

            stats = [
                ("Strength", data.strength), ("Dexterity", data.dexterity), 
                ("Constitution", data.constitution), ("Intelligence", data.intelligence),
                ("Wisdom", data.wisdom), ("Charisma", data.charisma)
            ]
            for name, value in stats:
                if value is not None and not (1 <= value <= max_stat_value):
                    raise ValueError(f"{name} ({value}) must be between 1 and {max_stat_value} for this tier status ({effective_is_ascended}).")
            if data.armor_class is not None and data.armor_class > max_ac_allowed:
                raise ValueError(f"Armor Class ({data.armor_class}) cannot exceed {max_ac_allowed} for this tier status ({effective_is_ascended}).")
            if data.hit_points_max is not None and data.hit_points_max > max_hp_allowed:
                raise ValueError(f"Max Hit Points ({data.hit_points_max}) cannot exceed {max_hp_allowed} for this tier status ({effective_is_ascended}).")
        return data


class CharacterInDBBase(CharacterBase):
    id: int
    user_id: int 
    created_at: datetime
    updated_at: datetime
    skills: List[CharacterSkillSchema] = []
    inventory_items: List[CharacterItemSchema] = []
    known_spells: List[CharacterSpellSchema] = []

    class Config:
        from_attributes = True

class Character(CharacterInDBBase):
    pass