# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
import random

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel

from app.schemas.character import CharacterCreate as CharacterCreateSchema
from app.schemas.character import CharacterUpdate as CharacterUpdateSchema
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema
from app.schemas.item import CharacterItemUpdate as CharacterItemUpdateSchema
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate
from app.schemas.admin import AdminCharacterProgressionUpdate # <--- NEW SCHEMA IMPORT

XP_THRESHOLDS = { 
    # ... (your extended XP_THRESHOLDS dictionary) ...
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
    9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
    15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
    21: 410000, 22: 470000, 23: 535000, 24: 605000, 25: 680000,
    26: 760000, 27: 845000, 28: 935000, 29: 1030000, 30: 1130000,
    31: 1240000, 32: 1360000, 33: 1490000, 34: 1630000, 35: 1780000,
    36: 1940000, 37: 2110000, 38: 2290000, 39: 2480000, 40: 2680000,
    41: 2900000, 42: 3140000, 43: 3400000, 44: 3680000, 45: 3980000,
    46: 4300000, 47: 4640000, 48: 5000000, 49: 5380000, 50: 5780000
}

CLASS_HIT_DIE_MAP = {
    # ... (your CLASS_HIT_DIE_MAP) ...
    "artificer": 8, "barbarian": 12, "bard": 8, "cleric": 8, "druid": 8,
    "fighter": 10, "monk": 8, "paladin": 10, "ranger": 10, "rogue": 8,
    "sorcerer": 6, "warlock": 8, "wizard": 6
}

def get_level_for_xp(xp: int, is_ascended_tier: bool = False) -> int: # ... (as before) ...
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold: current_level = level
        else: break 
    return max(1, current_level)

def get_xp_for_level(level: int) -> int:
    """Returns the minimum XP required for a given level."""
    return XP_THRESHOLDS.get(level, 0) # Default to 0 if level not in map (e.g. > 50)

def calculate_ability_modifier(score: Optional[int]) -> int: # ... (as before) ...
    if score is None: return 0
    return (score - 10) // 2

async def create_character_for_user( # ... (as before, with hit_die_type logic) ...
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int
) -> CharacterModel:
    character_data = character_in.model_dump() 
    hit_die_type_value = None
    if character_data.get("character_class"):
        hit_die_type_value = CLASS_HIT_DIE_MAP.get(character_data["character_class"].lower())
    character_data["hit_die_type"] = hit_die_type_value

    if character_data.get("experience_points") is not None:
        character_data["level"] = get_level_for_xp(character_data["experience_points"], character_data.get("is_ascended_tier", False))
    elif character_data.get("level") is None:
         character_data["level"] = 1

    initial_level = character_data["level"]
    character_data["hit_dice_total"] = initial_level
    character_data["hit_dice_remaining"] = initial_level
    character_data["death_save_successes"] = character_data.get("death_save_successes", 0) # From schema default
    character_data["death_save_failures"] = character_data.get("death_save_failures", 0) # From schema default
    character_data["has_pending_level_up"] = character_data.get("has_pending_level_up", False) # From schema default

    # Initial HP calculation
    if character_data.get("hit_points_max") is None and hit_die_type_value and character_data.get("constitution") is not None:
        con_modifier = calculate_ability_modifier(character_data["constitution"])
        if initial_level == 1:
            character_data["hit_points_max"] = hit_die_type_value + con_modifier
        else: # For characters created at higher than level 1
            hp = hit_die_type_value + con_modifier # HP for level 1
            for _ in range(2, initial_level + 1): # HP for subsequent levels (average)
                hp += max(1, (hit_die_type_value // 2) + 1 + con_modifier)
            character_data["hit_points_max"] = hp

    if character_data.get("hit_points_max") is not None and character_data.get("hit_points_current") is None:
        character_data["hit_points_current"] = character_data["hit_points_max"]

    db_character = CharacterModel(**character_data, user_id=user_id)
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)
    return await get_character(db, db_character.id)

async def get_character(db: AsyncSession, character_id: int) -> Optional[CharacterModel]: # ... (as before) ...
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
        )
        .filter(CharacterModel.id == character_id)
    )
    return result.scalars().first()

async def get_characters_by_user( # ... (as before) ...
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
        )
        .filter(CharacterModel.user_id == user_id)
        .order_by(CharacterModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_character( # ... (as before, with hit_die_type update logic) ...
    db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema
) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    if "character_class" in update_data and update_data["character_class"] is not None:
        new_class_name_lower = update_data["character_class"].lower()
        character.hit_die_type = CLASS_HIT_DIE_MAP.get(new_class_name_lower)
    for field, value in update_data.items():
        if field == "character_class" and "hit_die_type" in update_data:
            setattr(character, field, value)
        elif field != "hit_die_type": # Prevent direct update if not via class change
            setattr(character, field, value)
    if character.hit_points_current is not None and character.hit_points_max is not None:
        if character.hit_points_current > character.hit_points_max:
            character.hit_points_current = character.hit_points_max
    if character.hit_dice_remaining is not None and character.hit_dice_total is not None:
         if character.hit_dice_remaining > character.hit_dice_total:
            character.hit_dice_remaining = character.hit_dice_total
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def delete_character( # ... (as before) ...
    db: AsyncSession, character_id: int, user_id: int 
) -> Optional[CharacterModel]:
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete)
        await db.commit()
        return character_to_delete
    return None

async def award_xp_to_character( # ... (as before) ...
    db: AsyncSession, *, character: CharacterModel, xp_to_add: int
) -> CharacterModel:
    if xp_to_add <= 0:
        raise ValueError("XP to award must be a positive integer.")
    current_xp = character.experience_points if character.experience_points is not None else 0
    character.experience_points = current_xp + xp_to_add
    new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
    if new_level > character.level:
        print(f"Character {character.name} (ID: {character.id}) leveled up from {character.level} to {new_level}!")
        character.hit_dice_total = new_level 
        character.hit_dice_remaining = new_level 
        character.level = new_level
        character.has_pending_level_up = True 
        print(f"Character {character.name} is now level {character.level} and has a pending level-up.")
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def confirm_level_up_hp_increase( # ... (as before) ...
    db: AsyncSession, *, character: CharacterModel, method: str = "average"
) -> Tuple[CharacterModel, int]:
    if not character.has_pending_level_up:
        raise ValueError("Character does not have a pending level up to confirm HP for.")
    if not character.hit_die_type:
        raise ValueError("Character hit_die_type is not set. Cannot calculate HP.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_gained_from_die = 0
    if method == "average":
        hp_gained_from_die = (character.hit_die_type // 2) + 1
    elif method == "roll":
        hp_gained_from_die = random.randint(1, character.hit_die_type)
    else:
        raise ValueError("Invalid HP increase method. Choose 'average' or 'roll'.")
    hp_gained_this_level = max(1, hp_gained_from_die + con_modifier)
    current_max_hp = character.hit_points_max if character.hit_points_max is not None else 0
    character.hit_points_max = current_max_hp + hp_gained_this_level
    current_hp = character.hit_points_current if character.hit_points_current is not None else 0
    character.hit_points_current = min(current_hp + hp_gained_this_level, character.hit_points_max)
    character.has_pending_level_up = False 
    db.add(character)
    await db.commit()
    await db.refresh(character)
    updated_character = await get_character(db, character.id)
    if not updated_character: 
        raise Exception("Failed to reload character after HP increase.")
    return updated_character, hp_gained_this_level

async def spend_character_hit_die( # ... (as before) ...
    db: AsyncSession, *, character: CharacterModel, dice_roll_result: int
) -> CharacterModel:
    if character.hit_dice_remaining is None or character.hit_dice_remaining <= 0:
        raise ValueError("No hit dice remaining to spend.")
    if not character.hit_die_type:
        raise ValueError("Character hit_die_type is not set.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_healed = max(1, dice_roll_result + con_modifier)
    character.hit_dice_remaining -= 1
    current_hp = character.hit_points_current if character.hit_points_current is not None else 0
    max_hp = character.hit_points_max if character.hit_points_max is not None else current_hp
    character.hit_points_current = min(current_hp + hp_healed, max_hp)
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def record_death_save( # ... (as before) ...
    db: AsyncSession, *, character: CharacterModel, success: bool
) -> CharacterModel:
    if success:
        current_successes = character.death_save_successes if character.death_save_successes is not None else 0
        character.death_save_successes = min(current_successes + 1, 3)
    else:
        current_failures = character.death_save_failures if character.death_save_failures is not None else 0
        character.death_save_failures = min(current_failures + 1, 3)
    if character.death_save_successes >= 3 or character.death_save_failures >= 3:
        character.death_save_successes = 0
        character.death_save_failures = 0
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def reset_death_saves(db: AsyncSession, *, character: CharacterModel) -> CharacterModel: # ... (as before) ...
    character.death_save_successes = 0
    character.death_save_failures = 0
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

# --- NEW ADMIN FUNCTION for setting character progression ---
async def admin_update_character_progression(
    db: AsyncSession, 
    *, 
    character: CharacterModel, 
    progression_in: AdminCharacterProgressionUpdate
) -> CharacterModel:
    """
    Admin function to directly set a character's level and/or XP.
    Resets HP and Hit Dice according to the new level if level is changed.
    """
    updated = False

    if progression_in.level is not None:
        # Validate level against character's tier (using Pydantic validator for CharacterBase as reference)
        max_level = 50 if character.is_ascended_tier else 30
        if not (1 <= progression_in.level <= max_level):
            raise ValueError(f"Admin: Target level ({progression_in.level}) is outside the allowed range (1-{max_level}) for this character's tier.")

        character.level = progression_in.level
        character.experience_points = get_xp_for_level(character.level) # Set XP to minimum for that level

        # Reset HP and Hit Dice for the new level
        if character.hit_die_type and character.constitution is not None:
            con_mod = calculate_ability_modifier(character.constitution)
            # Calculate HP: Max at 1st level, average for subsequent levels
            new_max_hp = character.hit_die_type + con_mod # For level 1
            if character.level > 1:
                # Add average HP for levels 2 through new_level
                for _lvl in range(2, character.level + 1):
                    new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
            character.hit_points_max = new_max_hp
            character.hit_points_current = new_max_hp # Full heal on admin level set

        character.hit_dice_total = character.level
        character.hit_dice_remaining = character.level
        character.has_pending_level_up = False # Clear any pending state
        updated = True

    elif progression_in.experience_points is not None:
        # Only XP is provided, level will be derived
        character.experience_points = progression_in.experience_points
        new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)

        if new_level != character.level: # If this XP change also results in a level change
            # This logic mirrors award_xp_to_character without the "pending" state for admin set.
            character.level = new_level
            character.hit_dice_total = new_level
            character.hit_dice_remaining = new_level
            # HP would need to be recalculated based on all new levels gained.
            # This can become complex if multiple levels gained just from XP set.
            # For simplicity of admin override, if XP sets a new level, we might also just reset HP like above.
            if character.hit_die_type and character.constitution is not None:
                con_mod = calculate_ability_modifier(character.constitution)
                new_max_hp = character.hit_die_type + con_mod # Lvl 1
                if character.level > 1:
                    for _lvl in range(2, character.level + 1):
                        new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
                character.hit_points_max = new_max_hp
                character.hit_points_current = new_max_hp
            character.has_pending_level_up = False
        updated = True

    if updated:
        db.add(character)
        await db.commit()
        await db.refresh(character)

    return await get_character(db, character.id) # Return fully loaded character

# Ensure your existing skill, inventory, and spell management functions are here too
# ... (get_character_skill_association, assign_or_update_skill_proficiency_to_character, etc.) ...
# ... (get_character_inventory_item, add_item_to_character_inventory, etc.) ...
# ... (get_character_spell_association, add_spell_to_character, etc.) ...

