# Path: api/app/schemas/character.py
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List, Any, Dict 
from datetime import datetime

# Assuming these are correctly defined in their respective schema files
from .skill import CharacterSkill as CharacterSkillSchema
from .item import CharacterItem as CharacterItemSchema
from .character_spell import CharacterSpell as CharacterSpellSchema 
# Import the Enum for Roguish Archetype
from app.game_data.rogue_data import RoguishArchetypeEnum # <--- NEW IMPORT

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    roguish_archetype: Optional[RoguishArchetypeEnum] = None # <--- NEW FIELD

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

    hit_points_max: Optional[int] = Field(None, ge=1) 
    hit_points_current: Optional[int] = None 

    armor_class: Optional[int] = Field(None) 

    hit_die_type: Optional[int] = Field(None, ge=6, le=12)
    hit_dice_total: Optional[int] = Field(1, ge=0)
    hit_dice_remaining: Optional[int] = Field(1, ge=0)

    death_save_successes: Optional[int] = Field(0, ge=0, le=3)
    death_save_failures: Optional[int] = Field(0, ge=0, le=3)

    level_up_status: Optional[str] = Field(None, max_length=50)

    @model_validator(mode='after')
    def check_stats_based_on_tier(cls, data):
        # ... (your existing validator logic - no change needed here for archetype) ...
        if data is None: return data
        is_ascended = data.is_ascended_tier
        max_level = 50 if is_ascended else 30
        max_stat_value = 50 if is_ascended else 30
        max_ac_allowed = 80 if is_ascended else 40 
        max_hp_allowed = 5000 if is_ascended else 700 
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
        if data.hit_points_current is not None and data.hit_points_max is not None:
            if data.hit_points_current > data.hit_points_max:
                data.hit_points_current = min(data.hit_points_current, data.hit_points_max)
        if data.hit_dice_remaining is not None and data.hit_dice_total is not None:
            if data.hit_dice_remaining > data.hit_dice_total:
                raise ValueError(f"Remaining Hit Dice ({data.hit_dice_remaining}) cannot exceed Total Hit Dice ({data.hit_dice_total}).")
        return data

class CharacterCreate(CharacterBase):
    chosen_cantrip_ids: Optional[List[int]] = Field(None, description="List of spell IDs for initial cantrips (e.g., for Sorcerers at L1).")
    chosen_initial_spell_ids: Optional[List[int]] = Field(None, description="List of spell IDs for initial L1 spells known (e.g., for Sorcerers at L1).")
    # roguish_archetype will default to None from CharacterBase. 
    # It's chosen at L3 via a specific level-up endpoint.

class CharacterUpdate(BaseModel): 
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50) 
    # roguish_archetype is not directly updatable here by player; managed by level-up choice.
    # An admin might be able to change it via a different mechanism if needed.
    is_ascended_tier: Optional[bool] = None
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
    hit_dice_remaining: Optional[int] = Field(None, ge=0)
    death_save_successes: Optional[int] = Field(None, ge=0, le=3)
    death_save_failures: Optional[int] = Field(None, ge=0, le=3)

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_update_stats_based_on_tier(cls, data):
        # ... (your existing validator for CharacterUpdate) ...
        if data is None: return data
        if data.is_ascended_tier is not None:
            effective_is_ascended = data.is_ascended_tier 
            max_stat_value = 50 if effective_is_ascended else 30
            max_ac_allowed = 80 if effective_is_ascended else 40 
            max_hp_allowed = 5000 if effective_is_ascended else 700 
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
    # roguish_archetype is inherited from CharacterBase and will be included here

    class Config:
        from_attributes = True

class Character(CharacterInDBBase):
    pass

# --- Schemas for Leveling Up and Character State Management ---
class CharacterHPLevelUpRequest(BaseModel):
    method: str = Field("average", pattern="^(average|roll)$", description="Method to increase HP: 'average' or 'roll'")

class CharacterHPLevelUpResponse(BaseModel):
    character: Character 
    hp_gained: int
    level_up_message: str

class SpendHitDieRequest(BaseModel):
    dice_roll_result: int = Field(..., ge=1, description="The result of the hit die rolled by the player/client.")

class RecordDeathSaveRequest(BaseModel):
    success: bool

class ASISelectionRequest(BaseModel):
    stat_increases: Dict[str, int] = Field(..., description="Dictionary of stats to increase and by how much. E.g., {'strength': 2} or {'dexterity': 1, 'constitution': 1}")
    @model_validator(mode='after')
    def check_asi_rules(cls, data): # ... (your ASI validator as before) ...
        if data is None or not data.stat_increases: raise ValueError("stat_increases must be provided and contain data.")
        total_points_used = 0; stats_affected_count = 0
        valid_stat_names = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        for stat, increase in data.stat_increases.items():
            stat_lower = stat.lower()
            if stat_lower not in valid_stat_names: raise ValueError(f"Invalid stat name provided: '{stat}'. Must be one of {valid_stat_names}.")
            if increase not in [1, 2]: raise ValueError(f"Increase for {stat_lower} must be +1 or +2. Received: {increase}.")
            total_points_used += increase; stats_affected_count += 1
        if total_points_used != 2: raise ValueError(f"Total ability score increase must be +2 points. Used: {total_points_used}.")
        if stats_affected_count == 1:
            single_stat_increase_value = list(data.stat_increases.values())[0]
            if single_stat_increase_value != 2: raise ValueError("If increasing only one stat, it must be by +2.")
        elif stats_affected_count == 2:
            for increase_val in data.stat_increases.values():
                if increase_val != 1: raise ValueError("If increasing two stats, each must be by +1.")
        elif stats_affected_count > 2: raise ValueError("Cannot increase more than two ability scores with a standard ASI.")
        elif stats_affected_count == 0 and total_points_used != 2 : raise ValueError("stat_increases cannot be empty if total points used is not 2.")
        return data

class SorcererSpellSelectionRequest(BaseModel):
    new_leveled_spell_ids: Optional[List[int]] = Field(None, description="List of IDs for new LEVELED spells chosen to learn.")
    spell_to_replace_id: Optional[int] = Field(None, description="ID of a currently known spell to replace (optional).")
    replacement_spell_id: Optional[int] = Field(None, description="ID of the new spell to learn in place of the replaced one (required if spell_to_replace_id is provided).")
    chosen_cantrip_ids_on_level_up: Optional[List[int]] = Field(None, description="List of new cantrip IDs if character gains cantrips at this level.")
    @model_validator(mode='after')
    def check_replacement_logic(cls, data): # ... (validator as before) ...
        if data is None: return data
        if data.spell_to_replace_id is not None and data.replacement_spell_id is None:
            raise ValueError("If replacing a spell ('spell_to_replace_id' is provided), 'replacement_spell_id' must also be provided.")
        if data.spell_to_replace_id is None and data.replacement_spell_id is not None:
            raise ValueError("If providing a replacement spell ('replacement_spell_id'), 'spell_to_replace_id' must also be provided to indicate which spell is being replaced.")
        return data

class ExpertiseSelectionRequest(BaseModel):
    expert_skill_ids: List[int] = Field(..., min_length=2, max_length=2, description="List of exactly two unique skill IDs to gain expertise in. Character must be proficient in these skills.")
    @model_validator(mode='after')
    def check_distinct_skills(cls, data): # ... (validator as before) ...
        if data is None or data.expert_skill_ids is None: return data 
        if len(data.expert_skill_ids) != len(set(data.expert_skill_ids)):
            raise ValueError("Chosen skill IDs for expertise must be unique.")
        return data

# --- NEW SCHEMA for Rogue Archetype Selection ---
class RogueArchetypeSelectionRequest(BaseModel):
    archetype_name: RoguishArchetypeEnum # Player chooses one from the Enum

    