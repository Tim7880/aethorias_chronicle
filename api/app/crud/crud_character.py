# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple, Dict # Added Dict
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
from app.schemas.admin import AdminCharacterProgressionUpdate # Keep this if you have it

# --- XP, Leveling, ASI, and Hit Dice Definitions ---
XP_THRESHOLDS = { 
    # ... (your extended XP_THRESHOLDS dictionary up to level 50) ...
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
    "artificer": 8, "barbarian": 12, "bard": 8, "cleric": 8, "druid": 8,
    "fighter": 10, "monk": 8, "paladin": 10, "ranger": 10, "rogue": 8,
    "sorcerer": 6, "warlock": 8, "wizard": 6
}

# Standard D&D 5e ASI levels for most classes
# Fighters get more (6, 14), Rogues get one more (10)
# This map needs to be accurate for the classes you intend to support fully.
# For MVP, we can use a general list, or make it more detailed.
# Let's define a more general one, specific class features might grant more.
STANDARD_ASI_LEVELS = [4, 8, 12, 16, 19]
# More specific map (Example, can be expanded or moved to a game_data module)
CLASS_ASI_LEVELS_MAP: Dict[str, List[int]] = {
    "fighter": [4, 6, 8, 12, 14, 16, 19],
    "rogue": [4, 8, 10, 12, 16, 19],
    # Default for others (most classes)
    "default": [4, 8, 12, 16, 19]
}


def get_level_for_xp(xp: int, is_ascended_tier: bool = False) -> int:
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            current_level = level
        else:
            break 
    return max(1, current_level)

def get_xp_for_level(level: int) -> int:
    return XP_THRESHOLDS.get(level, 0)

def calculate_ability_modifier(score: Optional[int]) -> int:
    if score is None: return 0
    return (score - 10) // 2

def is_asi_due(character_class: Optional[str], new_level: int) -> bool:
    """Checks if a character is due for an ASI/Feat at their new level."""
    if not character_class:
        return False # Cannot determine without a class
    
    class_key = character_class.lower()
    asi_levels = CLASS_ASI_LEVELS_MAP.get(class_key, CLASS_ASI_LEVELS_MAP["default"])
    return new_level in asi_levels

# --- Character Core CRUD ---
async def create_character_for_user(
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int
) -> CharacterModel:
    character_data = character_in.model_dump() 
    
    hit_die_type_value = None
    if character_data.get("character_class"):
        hit_die_type_value = CLASS_HIT_DIE_MAP.get(character_data["character_class"].lower())
    character_data["hit_die_type"] = hit_die_type_value
    
    if character_data.get("experience_points") is not None:
        character_data["level"] = get_level_for_xp(
            character_data["experience_points"], 
            character_data.get("is_ascended_tier", False)
        )
    elif character_data.get("level") is None:
         character_data["level"] = 1
    
    initial_level = character_data["level"]
    character_data["hit_dice_total"] = initial_level
    character_data["hit_dice_remaining"] = initial_level
    character_data["death_save_successes"] = character_data.get("death_save_successes", 0)
    character_data["death_save_failures"] = character_data.get("death_save_failures", 0)
    
    character_data["level_up_status"] = None # Explicitly set to None on creation

    if initial_level == 1 and hit_die_type_value and character_data.get("constitution") is not None:
        con_modifier = calculate_ability_modifier(character_data["constitution"])
        character_data["hit_points_max"] = hit_die_type_value + con_modifier
        character_data["hit_points_current"] = character_data["hit_points_max"]
    else:
        if character_data.get("hit_points_max") is not None and character_data.get("hit_points_current") is None:
            character_data["hit_points_current"] = character_data["hit_points_max"]
            
    db_character = CharacterModel(**character_data, user_id=user_id)
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)
    return await get_character(db, db_character.id)


async def get_character(db: AsyncSession, character_id: int) -> Optional[CharacterModel]:
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

async def get_characters_by_user(
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

async def update_character(
    db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema
) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    if "character_class" in update_data and update_data["character_class"] is not None:
        new_class_name_lower = update_data["character_class"].lower()
        character.hit_die_type = CLASS_HIT_DIE_MAP.get(new_class_name_lower)
    for field, value in update_data.items():
        if field == "character_class" and "hit_die_type" in update_data:
            setattr(character, field, value)
        elif field not in ["level", "experience_points", "hit_die_type", "hit_dice_total", "level_up_status"]: # These are managed by specific processes
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

async def award_xp_to_character( # MODIFIED
    db: AsyncSession, *, character: CharacterModel, xp_to_add: int
) -> CharacterModel:
    if xp_to_add <= 0:
        raise ValueError("XP to award must be a positive integer.")

    current_xp = character.experience_points if character.experience_points is not None else 0
    character.experience_points = current_xp + xp_to_add
    
    new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
    
    if new_level > character.level:
        print(f"Character {character.name} (ID: {character.id}) is eligible for level {new_level} (was {character.level})!")
        character.level = new_level # Update level number
        character.hit_dice_total = new_level 
        character.hit_dice_remaining = new_level # Regain all hit dice on level up
        
        character.level_up_status = "pending_hp" # Set status for next step
        print(f"Character {character.name} is now level {character.level}. Status: {character.level_up_status}")
    else:
        # If no level gain, ensure level_up_status is None if it wasn't already
        if character.level_up_status is not None: # Only clear if it was set
            character.level_up_status = None 
            print(f"Character {character.name} XP updated. No level change. Level up status cleared.")


    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def confirm_level_up_hp_increase(
    db: AsyncSession, *, character: CharacterModel, method: str = "average"
) -> Tuple[CharacterModel, int]:
    """
    Processes HP increase for a character with a pending level up.
    Returns the updated character and the amount of HP gained.
    """
    # --- MODIFIED CHECK ---
    if character.level_up_status != "pending_hp":
        raise ValueError(f"Character is not pending HP confirmation for this stage. Current status: {character.level_up_status}")
    # --- END MODIFICATION ---
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
    
    # On level up, characters often regain all HP or at least the HP gained.
    # Let's set current HP to the new max.
    character.hit_points_current = character.hit_points_max
    
    # Transition to next level-up stage or clear status
    if is_asi_due(character.character_class, character.level):
        character.level_up_status = "pending_asi" # <--- USES NEW FIELD
        print(f"Character {character.name} HP increased by {hp_gained_this_level}. New Max HP: {character.hit_points_max}. Status set to: {character.level_up_status}")
    else:
        character.level_up_status = None # <--- USES NEW FIELD
        print(f"Character {character.name} HP increased by {hp_gained_this_level}. New Max HP: {character.hit_points_max}. Level up process complete for this stage.")

    db.add(character)
    await db.commit()
    await db.refresh(character)
    
    updated_character = await get_character(db, character.id)
    if not updated_character: 
        raise Exception("Failed to reload character after HP increase.")
            
    return updated_character, hp_gained_this_level

# --- Functions for Hit Dice & Death Saves Management (as before) ---
async def spend_character_hit_die(
    db: AsyncSession, *, character: CharacterModel, dice_roll_result: int
) -> CharacterModel:
    if character.hit_dice_remaining is None or character.hit_dice_remaining <= 0:
        raise ValueError("No hit dice remaining to spend.")
    if not character.hit_die_type:
        raise ValueError("Character hit_die_type is not set.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_healed = max(1, dice_roll_result + con_modifier) # Ensure at least 1 HP healed
    character.hit_dice_remaining -= 1
    current_hp = character.hit_points_current if character.hit_points_current is not None else 0
    max_hp = character.hit_points_max if character.hit_points_max is not None else current_hp
    character.hit_points_current = min(current_hp + hp_healed, max_hp)
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def record_death_save(
    db: AsyncSession, *, character: CharacterModel, success: bool
) -> CharacterModel:
    if success:
        current_successes = character.death_save_successes if character.death_save_successes is not None else 0
        character.death_save_successes = min(current_successes + 1, 3)
    else:
        current_failures = character.death_save_failures if character.death_save_failures is not None else 0
        character.death_save_failures = min(current_failures + 1, 3)
    if character.death_save_successes >= 3 or character.death_save_failures >= 3:
        print(f"Character {character.name} death save resolved: Successes={character.death_save_successes}, Failures={character.death_save_failures}. Resetting saves.")
        character.death_save_successes = 0
        character.death_save_failures = 0
        # Add logic here for character becoming stable (if 3 successes) or dying (if 3 failures)
        # For now, just resetting the counters.
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def reset_death_saves(db: AsyncSession, *, character: CharacterModel) -> CharacterModel:
    character.death_save_successes = 0
    character.death_save_failures = 0
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)



# --- Existing Skill, Inventory, Spell management functions follow ---
# (Make sure to paste your existing functions for skills, inventory, and spells here)
# ... (get_character_skill_association, assign_or_update_skill_proficiency_to_character, etc.) ...
# ... (get_character_inventory_item, add_item_to_character_inventory, etc.) ...
# ... (get_character_spell_association, add_spell_to_character, etc.) ...
