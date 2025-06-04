# Path: api/app/schemas/character.py
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, List, Any, Dict 
from datetime import datetime

# Assuming these are correctly defined and exported from their respective schema files
from .skill import CharacterSkill as CharacterSkillSchema
from .item import CharacterItem as CharacterItemSchema
from .character_spell import CharacterSpell as CharacterSpellSchema 
# Import the Enum for Roguish Archetype
from app.game_data.rogue_data import RoguishArchetypeEnum

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    roguish_archetype: Optional[RoguishArchetypeEnum] = None

    is_ascended_tier: bool = Field(default=False)
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

    # --- ADDED/UPDATED CURRENCY FIELDS ---
    currency_pp: Optional[int] = Field(0, ge=0, description="Platinum Pieces")
    currency_gp: Optional[int] = Field(0, ge=0, description="Gold Pieces")
    currency_ep: Optional[int] = Field(0, ge=0, description="Electrum Pieces")
    currency_sp: Optional[int] = Field(0, ge=0, description="Silver Pieces")
    currency_cp: Optional[int] = Field(0, ge=0, description="Copper Pieces")
    # --- END CURRENCY FIELDS ---
    
        # --- NEW SAVING THROW PROFICIENCY FIELDS ---
    st_prof_strength: bool = Field(default=False, description="Proficiency in Strength saving throws")
    st_prof_dexterity: bool = Field(default=False, description="Proficiency in Dexterity saving throws")
    st_prof_constitution: bool = Field(default=False, description="Proficiency in Constitution saving throws")
    st_prof_intelligence: bool = Field(default=False, description="Proficiency in Intelligence saving throws")
    st_prof_wisdom: bool = Field(default=False, description="Proficiency in Wisdom saving throws")
    st_prof_charisma: bool = Field(default=False, description="Proficiency in Charisma saving throws")
    # --- END NEW SAVING THROW PROFICIENCY FIELDS ---

    @model_validator(mode='after')
    def check_stats_based_on_tier(cls, data):
        if data is None: return data # Should not happen if model is instantiated
        # Ensure data is not None before accessing attributes
        is_ascended = data.is_ascended_tier if hasattr(data, 'is_ascended_tier') else False
        
        # Max level based on tier
        max_level = 50 if is_ascended else 30
        if hasattr(data, 'level') and data.level is not None and not (1 <= data.level <= max_level):
            raise ValueError(f"Level ({data.level}) must be between 1 and {max_level} for this tier.")

        # Max stat value based on tier
        max_stat_value = 50 if is_ascended else 30
        stats_to_check_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat_name in stats_to_check_names:
            value = getattr(data, stat_name, None)
            if value is not None and not (1 <= value <= max_stat_value):
                raise ValueError(f"{stat_name.capitalize()} ({value}) must be between 1 and {max_stat_value} for this tier.")

        # Max AC based on tier
        max_ac_allowed = 80 if is_ascended else 40 
        if hasattr(data, 'armor_class') and data.armor_class is not None and data.armor_class > max_ac_allowed:
            raise ValueError(f"Armor Class ({data.armor_class}) cannot exceed {max_ac_allowed} for this tier.")
        
        # Max HP based on tier
        max_hp_allowed = 5000 if is_ascended else 700 
        if hasattr(data, 'hit_points_max') and data.hit_points_max is not None and data.hit_points_max > max_hp_allowed:
            raise ValueError(f"Max Hit Points ({data.hit_points_max}) cannot exceed {max_hp_allowed} for this tier.")
        
        # Current HP cannot exceed Max HP
        if hasattr(data, 'hit_points_current') and data.hit_points_current is not None and \
           hasattr(data, 'hit_points_max') and data.hit_points_max is not None:
            if data.hit_points_current > data.hit_points_max:
                # Instead of raising error, cap it, or let API decide how to handle.
                # For Pydantic validation, raising an error is often clearer.
                # However, for CharacterBase which might be used to construct "final state", capping might be ok.
                # Let's stick to raising error for validation clarity.
                raise ValueError(f"Current Hit Points ({data.hit_points_current}) cannot exceed Max Hit Points ({data.hit_points_max}).")

        # Remaining Hit Dice cannot exceed Total Hit Dice
        if hasattr(data, 'hit_dice_remaining') and data.hit_dice_remaining is not None and \
           hasattr(data, 'hit_dice_total') and data.hit_dice_total is not None:
            if data.hit_dice_remaining > data.hit_dice_total:
                raise ValueError(f"Remaining Hit Dice ({data.hit_dice_remaining}) cannot exceed Total Hit Dice ({data.hit_dice_total}).")
        return data

class CharacterCreate(CharacterBase):
    chosen_cantrip_ids: Optional[List[int]] = Field(None, description="List of spell IDs for initial cantrips (e.g., for Sorcerers at L1).")
    chosen_initial_spell_ids: Optional[List[int]] = Field(None, description="List of spell IDs for initial L1 spells known (e.g., for Sorcerers at L1).")
    chosen_skill_proficiencies: Optional[List[int]] = Field(None, description="List of skill IDs chosen for initial proficiency.")
    # Currency fields will inherit defaults (0) from CharacterBase.
    # Starting currency will be set by CRUD logic based on class/background later.

class CharacterUpdate(BaseModel): 
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50) 
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
    hit_points_current: Optional[int] = None # Can be updated
    hit_points_max: Optional[int] = Field(None, ge=1) # Can be updated (e.g. by CON change, level up)
    armor_class: Optional[int] = Field(None)
    hit_dice_remaining: Optional[int] = Field(None, ge=0) # Player might update after spending
    death_save_successes: Optional[int] = Field(None, ge=0, le=3)
    death_save_failures: Optional[int] = Field(None, ge=0, le=3)

    # --- ADDED CURRENCY FIELDS for update ---
    currency_pp: Optional[int] = Field(None, ge=0)
    currency_gp: Optional[int] = Field(None, ge=0)
    currency_ep: Optional[int] = Field(None, ge=0)
    currency_sp: Optional[int] = Field(None, ge=0)
    currency_cp: Optional[int] = Field(None, ge=0)
    # --- END CURRENCY FIELDS ---
    
    # --- ADDED SAVING THROW PROFICIENCIES for update ---
    st_prof_strength: Optional[bool] = None
    st_prof_dexterity: Optional[bool] = None
    st_prof_constitution: Optional[bool] = None
    st_prof_intelligence: Optional[bool] = None
    st_prof_wisdom: Optional[bool] = None
    st_prof_charisma: Optional[bool] = None
    # --- END SAVING THROW PROFICIENCIES ---

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_update_fields_against_tier(cls, data): # Renamed for clarity
        # This validator is for CharacterUpdate. It only knows about fields in CharacterUpdate.
        # If is_ascended_tier is not in the update payload, we can't validate other stats against it
        # without knowing the character's *current* tier from the database.
        # The more robust validation of the *final state* happens in the API endpoint
        # where current DB data is merged with update_payload and validated against CharacterBase.
        # This validator here primarily ensures that if is_ascended_tier IS changed,
        # any *other stats also present in this update payload* adhere to the new tier.
        if data is None: return data

        if hasattr(data, 'is_ascended_tier') and data.is_ascended_tier is not None:
            # Only apply strict tier checks if is_ascended_tier is part of this specific update
            effective_is_ascended = data.is_ascended_tier
            max_stat_value = 50 if effective_is_ascended else 30
            max_ac_allowed = 80 if effective_is_ascended else 40 
            max_hp_allowed = 5000 if effective_is_ascended else 700 

            stats_to_check_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            for stat_name in stats_to_check_names:
                value = getattr(data, stat_name, None)
                if value is not None and not (1 <= value <= max_stat_value):
                    raise ValueError(f"{stat_name.capitalize()} ({value}) must be between 1 and {max_stat_value} for this tier status ({effective_is_ascended}).")
            
            if hasattr(data, 'armor_class') and data.armor_class is not None and data.armor_class > max_ac_allowed:
                raise ValueError(f"Armor Class ({data.armor_class}) cannot exceed {max_ac_allowed} for this tier status ({effective_is_ascended}).")
            
            if hasattr(data, 'hit_points_max') and data.hit_points_max is not None and data.hit_points_max > max_hp_allowed:
                raise ValueError(f"Max Hit Points ({data.hit_points_max}) cannot exceed {max_hp_allowed} for this tier status ({effective_is_ascended}).")
        
        # Validate current HP against max HP if both are present in the update
        if hasattr(data, 'hit_points_current') and data.hit_points_current is not None and \
           hasattr(data, 'hit_points_max') and data.hit_points_max is not None:
            if data.hit_points_current > data.hit_points_max:
                 raise ValueError(f"Current Hit Points ({data.hit_points_current}) cannot exceed Max Hit Points ({data.hit_points_max}) in this update.")
        elif hasattr(data, 'hit_points_current') and data.hit_points_current is not None and \
             not hasattr(data, 'hit_points_max'): # If only current HP is updated, it cannot exceed existing character.hit_points_max
             # This check needs the existing character's max HP, so it's better done in the API endpoint logic
             # or by ensuring that if current_hp is updated, max_hp is also provided if it's meant to change.
             pass


        # Validate hit_dice_remaining against hit_dice_total if both are in update
        # This also needs existing character.hit_dice_total if only remaining is updated.
        # For now, Field(ge=0) handles basic validation.
        if hasattr(data, 'hit_dice_remaining') and data.hit_dice_remaining is not None and \
           hasattr(data, 'hit_dice_total') and data.hit_dice_total is not None: # If total is also being updated
             if data.hit_dice_remaining > data.hit_dice_total:
                raise ValueError(f"Remaining Hit Dice ({data.hit_dice_remaining}) cannot exceed Total Hit Dice ({data.hit_dice_total}) in this update.")

        return data

class CharacterInDBBase(CharacterBase):
    id: int
    user_id: int 
    created_at: datetime
    updated_at: datetime
    skills: List[CharacterSkillSchema] = []
    inventory_items: List[CharacterItemSchema] = []
    known_spells: List[CharacterSpellSchema] = []
    # All currency fields are inherited from CharacterBase

    class Config:
        from_attributes = True

class Character(CharacterInDBBase):
    pass

# --- Schemas for Leveling Up and Character Actions ---
class CharacterHPLevelUpRequest(BaseModel):
    method: str = Field("average", pattern="^(average|roll)$")

class CharacterHPLevelUpResponse(BaseModel):
    character: Character 
    hp_gained: int
    level_up_message: str

class SpendHitDieRequest(BaseModel):
    dice_roll_result: int = Field(..., ge=1)

class RecordDeathSaveRequest(BaseModel):
    success: bool

class ASISelectionRequest(BaseModel):
    stat_increases: Dict[str, int] = Field(...)
    @model_validator(mode='after')
    def check_asi_rules(cls, data):
        if data is None or not data.stat_increases: raise ValueError("stat_increases must be provided.")
        total_points_used = 0; stats_affected_count = 0
        valid_stat_names = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        for stat, increase in data.stat_increases.items():
            stat_lower = stat.lower()
            if stat_lower not in valid_stat_names: raise ValueError(f"Invalid stat name: '{stat}'.")
            if increase not in [1, 2]: raise ValueError(f"Increase for {stat_lower} must be +1 or +2.")
            total_points_used += increase; stats_affected_count += 1
        if total_points_used != 2: raise ValueError(f"Total ASI must be +2 points. Used: {total_points_used}.")
        if stats_affected_count == 1 and list(data.stat_increases.values())[0] != 2: raise ValueError("If one stat, must be +2.")
        elif stats_affected_count == 2:
            for increase_val in data.stat_increases.values():
                if increase_val != 1: raise ValueError("If two stats, each must be by +1.")
        elif stats_affected_count > 2: raise ValueError("Cannot increase more than two scores.")
        elif stats_affected_count == 0 and total_points_used !=2 : raise ValueError("stat_increases cannot be empty.")
        return data

class SorcererSpellSelectionRequest(BaseModel):
    new_leveled_spell_ids: Optional[List[int]] = Field(None)
    spell_to_replace_id: Optional[int] = Field(None)
    replacement_spell_id: Optional[int] = Field(None)
    chosen_cantrip_ids_on_level_up: Optional[List[int]] = Field(None)
    @model_validator(mode='after')
    def check_replacement_logic(cls, data):
        if data is None: return data
        if data.spell_to_replace_id is not None and data.replacement_spell_id is None:
            raise ValueError("If replacing a spell, 'replacement_spell_id' must be provided.")
        if data.spell_to_replace_id is None and data.replacement_spell_id is not None:
            raise ValueError("If providing a replacement spell, 'spell_to_replace_id' must also be provided.")
        return data

class ExpertiseSelectionRequest(BaseModel):
    expert_skill_ids: List[int] = Field(..., min_length=2, max_length=2)
    @model_validator(mode='after')
    def check_distinct_skills(cls, data):
        if data is None or data.expert_skill_ids is None: return data 
        if len(data.expert_skill_ids) != len(set(data.expert_skill_ids)):
            raise ValueError("Chosen skill IDs for expertise must be unique.")
        return data

class RogueArchetypeSelectionRequest(BaseModel):
    archetype_name: RoguishArchetypeEnum

    