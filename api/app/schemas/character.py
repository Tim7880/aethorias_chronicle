# Path: api/app/schemas/character.py
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Any # Any for other potential flexible fields if used elsewhere
from datetime import datetime

from .skill import CharacterSkill as CharacterSkillSchema
from .item import CharacterItem as CharacterItemSchema
from .character_spell import CharacterSpell as CharacterSpellSchema

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    
    # --- ASCENDED TIER FIELD ---
    is_ascended_tier: bool = False # Defaults to False for new characters

    level: Optional[int] = Field(1, ge=1) # Initial lower bound
    experience_points: Optional[int] = Field(0, ge=0)
    alignment: Optional[str] = Field(None, max_length=50)
    background_story: Optional[str] = None
    appearance_description: Optional[str] = None

    strength: Optional[int] = Field(10, ge=1) # Initial lower bound
    dexterity: Optional[int] = Field(10, ge=1)
    constitution: Optional[int] = Field(10, ge=1)
    intelligence: Optional[int] = Field(10, ge=1)
    wisdom: Optional[int] = Field(10, ge=1)
    charisma: Optional[int] = Field(10, ge=1)

    hit_points_current: Optional[int] = None
    hit_points_max: Optional[int] = Field(None, ge=1) # If set, must be at least 1
    armor_class: Optional[int] = Field(None) # No hard min/max here, validator handles max

    @model_validator(mode='after')
    def check_stats_based_on_tier(cls, data): # data is the model instance here
        if data is None: # Should not happen if called on an instance
            return data

        is_ascended = data.is_ascended_tier
        
        # Define limits based on tier
        max_level = 50 if is_ascended else 30
        max_stat_value = 50 if is_ascended else 30
        # User guidelines: Ascended AC > 50, HP > 700. 
        # For schema validation, we'll set generous upper caps.
        # Normal tier practical max for schema validation (can be adjusted):
        max_ac_allowed = 80 if is_ascended else 40 # e.g. Max AC for ascended, practical max for normal
        max_hp_allowed = 2500 if is_ascended else 700 # e.g. Max HP for ascended, practical max for normal

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

        # AC: User guideline "over 50" for ascended. No specific upper bound mentioned.
        # We set a schema upper bound (max_ac_allowed) mainly for data sanity.
        if data.armor_class is not None and data.armor_class > max_ac_allowed:
            raise ValueError(f"Armor Class ({data.armor_class}) cannot exceed {max_ac_allowed} for this tier.")
        
        # HP: User guideline "over 700" for ascended.
        if data.hit_points_max is not None and data.hit_points_max > max_hp_allowed:
            raise ValueError(f"Max Hit Points ({data.hit_points_max}) cannot exceed {max_hp_allowed} for this tier.")
        
        return data


class CharacterCreate(CharacterBase):
    # Inherits is_ascended_tier (default False) and the validator from CharacterBase.
    # A regular user creating a character cannot set is_ascended_tier to True.
    # If is_ascended_tier were True here, validation would use ascended limits.
    pass


class CharacterUpdate(BaseModel): # All fields optional
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    
    # --- ASCENDED TIER FIELD (updatable) ---
    is_ascended_tier: Optional[bool] = None # Allows changing the tier status

    level: Optional[int] = Field(None, ge=1)
    experience_points: Optional[int] = Field(None, ge=0)
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

    @model_validator(mode='after')
    def check_update_stats_based_on_tier(cls, data): # data is the model instance
        if data is None:
            return data
            
        # For CharacterUpdate, is_ascended_tier might not be in the payload if not being changed.
        # If it is in the payload, that's the value we use for validation.
        # If it's NOT in the payload, we'd ideally need the character's *current*
        # is_ascended_tier status from the DB to validate other incoming fields.
        # This validator runs *after* initial field validation and model creation.
        #
        # A simple approach for CharacterUpdate: if is_ascended_tier is provided, use it.
        # If not, the other fields are just validated against their basic Field constraints (e.g. ge=1).
        # The more complex validation happens if is_ascended_tier is *part* of the update,
        # or if we always enforce based on the *resulting* state.
        #
        # Let's assume this validator applies to the fields *present in the update*.
        # The API endpoint will need to fetch the character first to know its current tier
        # if `is_ascended_tier` is not part of the update payload but other stats are.
        #
        # For simplicity in this @model_validator, if `is_ascended_tier` is not explicitly being
        # set in this update, we can't reliably perform the tier-based validation for other
        # fields *within this Pydantic validator alone* without knowing the original state.
        #
        # However, a common pattern is that the validator validates the *final state* if all
        # necessary fields (like is_ascended_tier) are available or defaulted.
        #
        # Let's refine CharacterUpdate: It should reflect the final state.
        # The API layer will construct the CharacterUpdate object potentially merging
        # with existing data if needed, or the validator needs access to original character.
        # The simplest for Pydantic is to validate the given data.
        # If is_ascended_tier is None (not provided in update), we can't do tier-specific validation.
        # But if it *is* provided, or if other stats are provided, we should validate against the
        # *effective* tier.
        #
        # The most robust way is for the API endpoint to:
        # 1. Load the existing character.
        # 2. Create an updated data dictionary by applying request changes.
        # 3. Validate this complete, updated data dictionary using CharacterBase's logic.
        #
        # Given Pydantic's design, a validator on CharacterUpdate will only see the fields
        # passed in the update. Let's make it so that if is_ascended_tier is passed,
        # the other stats are validated against it. If it's NOT passed, other stats
        # are only validated against their basic ge=1.
        #
        # A better approach for CharacterUpdate: reuse the CharacterBase validator logic
        # but requires knowing the character's tier (either from payload or DB).
        # The API endpoint is better suited to prepare the full "to-be" state and validate it.
        # For now, CharacterUpdate will just have its field definitions. The actual
        # conditional validation will effectively be handled when CharacterBase's
        # logic is applied to the *complete* character data (original + update)
        # in the API route before calling CRUD.
        #
        # So, the @model_validator on CharacterBase will be the primary enforcer.
        # CharacterUpdate just defines which fields are updatable.
        # The API route for PUT will be responsible for:
        # 1. Getting current character data.
        # 2. Applying updates from request.
        # 3. Re-validating the *entire new state* (e.g. by constructing a CharacterBase from it).

        # Let's simplify `CharacterUpdate`'s own validator for now or remove it,
        # relying on `CharacterBase`'s validator when the full object is considered.
        # For direct use of CharacterUpdate, if is_ascended_tier is present, it implies a context.
        
        # Re-using CharacterBase's logic is cleaner if possible.
        # The provided `is_ascended_tier` in the update payload takes precedence.
        # If `is_ascended_tier` is not in the payload, this validator can't know the tier
        # unless we pass the original character data into the validation context, which is advanced.
        
        # For now, let's assume CharacterUpdate might be validated with context or this validator
        # is primarily for when is_ascended_tier IS part of the update.
        # If other stats are updated, their validation against the *correct* tier
        # will rely on the API endpoint combining data and re-validating using CharacterBase.
        # This internal validator is more for the case where is_ascended_tier is explicitly set.

        effective_is_ascended = data.is_ascended_tier # This will be None if not in update payload
        
        # If is_ascended_tier is not being changed, this validator on CharacterUpdate
        # cannot enforce tier-specific limits for other fields without knowing the original tier.
        # So, we only apply strict validation here if is_ascended_tier is provided in the update.
        if effective_is_ascended is not None:
            max_level = 50 if effective_is_ascended else 30
            max_stat_value = 50 if effective_is_ascended else 30
            max_ac_allowed = 80 if effective_is_ascended else 40 
            max_hp_allowed = 2500 if effective_is_ascended else 700

            if data.level is not None and not (1 <= data.level <= max_level):
                raise ValueError(f"Level ({data.level}) must be between 1 and {max_level} for this tier status ({effective_is_ascended}).")

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
    user_id: int # Owner
    created_at: datetime
    updated_at: datetime
    
    skills: List[CharacterSkillSchema] = []
    inventory_items: List[CharacterItemSchema] = []
    known_spells: List[CharacterSpellSchema] = []

    class Config:
        from_attributes = True

class Character(CharacterInDBBase): # This IS our main Character response schema
    pass




