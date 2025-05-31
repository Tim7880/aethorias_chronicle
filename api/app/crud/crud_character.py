# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func # <--- ENSURE func IS IMPORTED
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple, Dict
import random

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel

from app.schemas.character import (
    CharacterCreate as CharacterCreateSchema,
    CharacterUpdate as CharacterUpdateSchema,
    ASISelectionRequest,
    SorcererSpellSelectionRequest
)
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema # Not directly used here currently
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema
from app.schemas.item import CharacterItemUpdate as CharacterItemUpdateSchema
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate # Ensure these are defined
from app.schemas.admin import AdminCharacterProgressionUpdate

# --- Game Data Imports ---
from app.game_data.sorcerer_progression import (
    SORCERER_SPELLS_KNOWN_TABLE,
    get_sorcerer_max_spell_level_can_learn
)

# --- XP, Leveling, ASI, and Hit Dice Definitions ---
XP_THRESHOLDS = { 
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

CLASS_ASI_LEVELS_MAP: Dict[str, List[int]] = {
    "fighter": [4, 6, 8, 12, 14, 16, 19],
    "rogue": [4, 8, 10, 12, 16, 19],
    "default": [4, 8, 12, 16, 19] 
}

def get_level_for_xp(xp: int, is_ascended_tier: bool = False) -> int:
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold: current_level = level
        else: break 
    return max(1, current_level)

def get_xp_for_level(level: int) -> int:
    return XP_THRESHOLDS.get(level, 0)

def calculate_ability_modifier(score: Optional[int]) -> int:
    if score is None: return 0
    return (score - 10) // 2

def is_asi_due(character_class_name: Optional[str], new_level: int) -> bool:
    if not character_class_name: return False 
    class_key = character_class_name.lower()
    asi_levels = CLASS_ASI_LEVELS_MAP.get(class_key, CLASS_ASI_LEVELS_MAP.get("default", []))
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
        character_data["level"] = get_level_for_xp(character_data["experience_points"], character_data.get("is_ascended_tier", False))
    elif character_data.get("level") is None:
         character_data["level"] = 1
    initial_level = character_data["level"]
    character_data["hit_dice_total"] = initial_level
    character_data["hit_dice_remaining"] = initial_level
    character_data["death_save_successes"] = character_data.get("death_save_successes", 0)
    character_data["death_save_failures"] = character_data.get("death_save_failures", 0)
    character_data["level_up_status"] = None
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
        if field == "character_class" and "hit_die_type" in update_data: # Already handled hit_die_type if class changed
            setattr(character, field, value)
        elif field not in ["level", "experience_points", "hit_die_type", "hit_dice_total", "level_up_status"]:
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

async def delete_character(
    db: AsyncSession, character_id: int, user_id: int 
) -> Optional[CharacterModel]:
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete)
        await db.commit()
        return character_to_delete
    return None

async def award_xp_to_character(
    db: AsyncSession, *, character: CharacterModel, xp_to_add: int
) -> CharacterModel:
    if xp_to_add <= 0: raise ValueError("XP to award must be a positive integer.")
    current_xp = character.experience_points if character.experience_points is not None else 0
    character.experience_points = current_xp + xp_to_add
    new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
    if new_level > character.level:
        print(f"Character {character.name} (ID: {character.id}) is eligible for level {new_level} (was {character.level})!")
        character.level = new_level 
        character.hit_dice_total = new_level 
        character.hit_dice_remaining = new_level 
        character.level_up_status = "pending_hp"
        print(f"Character {character.name} is now level {character.level}. Status: {character.level_up_status}")
    else:
        if character.level_up_status is not None: character.level_up_status = None; print(f"Character {character.name} XP updated. No level change. Level up status cleared.")
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def confirm_level_up_hp_increase(
    db: AsyncSession, *, character: CharacterModel, method: str = "average"
) -> Tuple[CharacterModel, int]:
    if character.level_up_status != "pending_hp": raise ValueError(f"Character is not pending HP confirmation. Current status: {character.level_up_status}")
    if not character.hit_die_type: raise ValueError("Character hit_die_type is not set. Cannot calculate HP.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_gained_from_die = (character.hit_die_type // 2) + 1 if method == "average" else random.randint(1, character.hit_die_type)
    if method not in ["average", "roll"]: raise ValueError("Invalid HP increase method. Choose 'average' or 'roll'.")
    hp_gained_this_level = max(1, hp_gained_from_die + con_modifier)
    current_max_hp = character.hit_points_max if character.hit_points_max is not None else 0
    character.hit_points_max = current_max_hp + hp_gained_this_level
    character.hit_points_current = character.hit_points_max
    if is_asi_due(character.character_class, character.level): character.level_up_status = "pending_asi"
    elif character.character_class and character.character_class.lower() == "sorcerer": # Check for sorcerer spell progression next
        character.level_up_status = "pending_spells"
    # TODO: Add checks for other class features if they require player choice
    else: character.level_up_status = None 
    print(f"Character {character.name} HP increased by {hp_gained_this_level}. New Max HP: {character.hit_points_max}. Status set to: {character.level_up_status}")
    db.add(character); await db.commit(); await db.refresh(character)
    updated_character = await get_character(db, character.id)
    if not updated_character: raise Exception("Failed to reload character after HP increase.")
    return updated_character, hp_gained_this_level

async def apply_character_asi(
    db: AsyncSession, *, character: CharacterModel, asi_selection: ASISelectionRequest
) -> CharacterModel:
    if character.level_up_status != "pending_asi": raise ValueError(f"Character is not pending ASI selection. Current status: {character.level_up_status}")
    max_stat_for_tier = 50 if character.is_ascended_tier else 30 
    for stat_name_str, increase_amount in asi_selection.stat_increases.items():
        stat_name_lower = stat_name_str.lower() # Ensure lowercase for getattr
        current_score = getattr(character, stat_name_lower, None)
        if current_score is None: raise ValueError(f"Invalid stat name '{stat_name_str}' for ASI.")
        new_score = current_score + increase_amount
        if new_score > max_stat_for_tier:
            raise ValueError(f"ASI for {stat_name_str} to {new_score} would exceed tier maximum of {max_stat_for_tier}.")
        setattr(character, stat_name_lower, new_score)
        print(f"Character {character.name} {stat_name_str} increased by {increase_amount} to {new_score}.")
    
    if character.character_class and character.character_class.lower() == "sorcerer":
        character.level_up_status = "pending_spells"
    # TODO: Add checks for other class features if they require player choice
    else:
        character.level_up_status = None
    print(f"Character {character.name} ASI applied. Level up status set to: {character.level_up_status}")
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

# --- Character Skill Management Functions ---
async def get_character_skill_association(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    result = await db.execute(
        select(CharacterSkillModel).filter_by(character_id=character_id, skill_id=skill_id)
    )
    return result.scalars().first()

async def assign_or_update_skill_proficiency_to_character(
    db: AsyncSession, *, character_id: int, skill_id: int, is_proficient: bool
) -> CharacterSkillModel:
    # ... (existing code)
    skill_result = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
    if not skill_result.scalars().first(): raise ValueError(f"Skill with id {skill_id} not found.") 
    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)
    if db_char_skill: db_char_skill.is_proficient = is_proficient
    else: db_char_skill = CharacterSkillModel(character_id=character_id, skill_id=skill_id, is_proficient=is_proficient)
    db.add(db_char_skill); await db.commit(); await db.refresh(db_char_skill)
    result_with_skill_def = await db.execute(select(CharacterSkillModel).options(selectinload(CharacterSkillModel.skill_definition)).filter(CharacterSkillModel.id == db_char_skill.id))
    return result_with_skill_def.scalars().first()


async def remove_skill_from_character(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    # ... (existing code)
    db_char_skill_to_delete = await db.execute(select(CharacterSkillModel).options(selectinload(CharacterSkillModel.skill_definition)).filter_by(character_id=character_id, skill_id=skill_id))
    db_char_skill = db_char_skill_to_delete.scalars().first()
    if db_char_skill: await db.delete(db_char_skill); await db.commit(); return db_char_skill
    return None

# --- Character Inventory Item Management Functions ---
async def get_character_inventory_item( # ... (existing code)
    db: AsyncSession, *, character_id: int, item_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).filter_by(character_id=character_id, item_id=item_id))
    return result.scalars().first()

async def add_item_to_character_inventory( # ... (existing code)
    db: AsyncSession, *, character_id: int, item_in: CharacterItemCreateSchema
) -> CharacterItemModel:
    item_definition_res = await db.execute(select(ItemModel).filter(ItemModel.id == item_in.item_id))
    if not item_definition_res.scalars().first(): raise ValueError(f"Item with ID {item_in.item_id} not found.")
    db_character_item = await get_character_inventory_item(db=db, character_id=character_id, item_id=item_in.item_id)
    if db_character_item: db_character_item.quantity += item_in.quantity
    else: db_character_item = CharacterItemModel(character_id=character_id, item_id=item_in.item_id, quantity=item_in.quantity, is_equipped=item_in.is_equipped)
    db.add(db_character_item); await db.commit(); await db.refresh(db_character_item)
    result_with_item_def = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == db_character_item.id))
    return result_with_item_def.scalars().first()


async def update_character_inventory_item( # ... (existing code)
    db: AsyncSession, *, character_item_id: int, item_in: CharacterItemUpdateSchema, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if not db_character_item: return None
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items(): setattr(db_character_item, field, value)
    if db_character_item.quantity <= 0: await db.delete(db_character_item); await db.commit(); return None 
    else: db.add(db_character_item); await db.commit(); await db.refresh(db_character_item); return db_character_item

async def remove_item_from_character_inventory( # ... (existing code)
    db: AsyncSession, *, character_item_id: int, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if db_character_item: await db.delete(db_character_item); await db.commit(); return db_character_item
    return None


# --- Character Spell Management Functions ---
async def get_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    result = await db.execute(
        select(CharacterSpellModel).filter_by(character_id=character_id, spell_id=spell_id)
    )
    return result.scalars().first()

async def add_spell_to_character( # Ensure this takes CharacterSpellCreate as input
    db: AsyncSession, *, character_id: int, spell_association_in: CharacterSpellCreate
) -> CharacterSpellModel:
    spell_def = await db.get(SpellModel, spell_association_in.spell_id)
    if not spell_def: raise ValueError(f"Spell definition with ID {spell_association_in.spell_id} not found")
    
    existing_assoc = await get_character_spell_association(db, character_id=character_id, spell_id=spell_association_in.spell_id)
    if existing_assoc:
        # Update existing if flags are different, otherwise it's already known/prepared as requested
        changed = False
        if spell_association_in.is_known is not None and existing_assoc.is_known != spell_association_in.is_known:
            existing_assoc.is_known = spell_association_in.is_known
            changed = True
        if spell_association_in.is_prepared is not None and existing_assoc.is_prepared != spell_association_in.is_prepared:
            existing_assoc.is_prepared = spell_association_in.is_prepared
            changed = True
        if not changed: # No change, just return existing fully loaded
            return await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == existing_assoc.id)).scalars().first()
        db_character_spell = existing_assoc
    else:
        db_character_spell = CharacterSpellModel(
            character_id=character_id,
            spell_id=spell_association_in.spell_id,
            is_known=spell_association_in.is_known if spell_association_in.is_known is not None else False, # Default to False if not provided
            is_prepared=spell_association_in.is_prepared if spell_association_in.is_prepared is not None else False # Default to False
        )
    db.add(db_character_spell)
    await db.commit()
    await db.refresh(db_character_spell)
    result_with_spell_def = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter(CharacterSpellModel.id == db_character_spell.id)
    )
    return result_with_spell_def.scalars().first()

async def update_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int, spell_association_update_in: CharacterSpellUpdate
) -> Optional[CharacterSpellModel]:
    db_char_spell = await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    if not db_char_spell: return None
    update_data = spell_association_update_in.model_dump(exclude_unset=True)
    if not update_data: return await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == db_char_spell.id)).scalars().first() # Return as is if no update data
    for field, value in update_data.items():
        setattr(db_char_spell, field, value)
    db.add(db_char_spell)
    await db.commit()
    await db.refresh(db_char_spell)
    result_with_spell_def = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter(CharacterSpellModel.id == db_char_spell.id)
    )
    return result_with_spell_def.scalars().first()

async def remove_spell_from_character(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    db_char_spell_to_delete = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter_by(character_id=character_id, spell_id=spell_id)
    )
    db_character_spell = db_char_spell_to_delete.scalars().first()
    if db_character_spell:
        await db.delete(db_character_spell)
        await db.commit()
        return db_character_spell
    return None

# --- NEW FUNCTION for Applying Sorcerer Spell Selections ---
async def apply_sorcerer_spell_selections(
    db: AsyncSession,
    *,
    character: CharacterModel,
    spell_selection: SorcererSpellSelectionRequest
) -> CharacterModel:
    if not character.character_class or character.character_class.lower() != "sorcerer":
        raise ValueError("This spell selection process is only for Sorcerers.")
    if character.level_up_status != "pending_spells":
        raise ValueError(f"Character is not pending spell selection. Current status: {character.level_up_status}")

    char_level = character.level
    
    # Determine current known spells (level 1+) before any changes this level up
    # This needs to be based on the state *before* this function makes changes.
    # A simple way is to query the DB for current known spells.
    pre_selection_known_spells_q = await db.execute(
        select(CharacterSpellModel.spell_id)
        .join(SpellModel, CharacterSpellModel.spell_id == SpellModel.id)
        .filter(CharacterSpellModel.character_id == character.id, 
                CharacterSpellModel.is_known == True, 
                SpellModel.level > 0)
    )
    pre_selection_known_spell_ids = {row[0] for row in pre_selection_known_spells_q.all()}
    current_known_spells_count = len(pre_selection_known_spell_ids)

    # Spells known at current (new) level and previous level
    _, num_spells_target_at_new_level = SORCERER_SPELLS_KNOWN_TABLE.get(char_level, (0, 0))
    num_spells_known_at_previous_level = 0
    if char_level > 1:
        _, num_spells_known_at_previous_level = SORCERER_SPELLS_KNOWN_TABLE.get(char_level - 1, (0, 0))
    
    spells_to_learn_this_level = num_spells_target_at_new_level - num_spells_known_at_previous_level
    
    max_spell_level_learnable = get_sorcerer_max_spell_level_can_learn(char_level)
    
    # --- Handle Spell Replacement First (if any) ---
    if spell_selection.spell_to_replace_id is not None and spell_selection.replacement_spell_id is not None:
        if spell_selection.spell_to_replace_id == spell_selection.replacement_spell_id:
            raise ValueError("Cannot replace a spell with itself.")

        # Verify spell_to_replace_id is known and is not a cantrip
        spell_to_replace_model = await db.get(SpellModel, spell_selection.spell_to_replace_id)
        if not spell_to_replace_model or spell_to_replace_model.level == 0:
             raise ValueError(f"Spell to replace (ID: {spell_selection.spell_to_replace_id}) is a cantrip or does not exist.")
        if spell_selection.spell_to_replace_id not in pre_selection_known_spell_ids:
            raise ValueError(f"Spell to replace (ID: {spell_selection.spell_to_replace_id}) is not currently known by the character.")

        # Validate the replacement spell
        replacement_spell_model = await db.get(SpellModel, spell_selection.replacement_spell_id)
        if not replacement_spell_model:
            raise ValueError(f"Chosen replacement spell with ID {spell_selection.replacement_spell_id} not found.")
        if replacement_spell_model.level == 0 or replacement_spell_model.level > max_spell_level_learnable:
            raise ValueError(f"Replacement spell '{replacement_spell_model.name}' is of invalid level ({replacement_spell_model.level}) for a level {char_level} Sorcerer.")
        if not (replacement_spell_model.dnd_classes and "sorcerer" in [c.lower() for c in replacement_spell_model.dnd_classes]):
            raise ValueError(f"Replacement spell '{replacement_spell_model.name}' is not a Sorcerer spell.")
        if replacement_spell_model.id in pre_selection_known_spell_ids and replacement_spell_model.id != spell_selection.spell_to_replace_id :
            raise ValueError(f"Character already knows the replacement spell '{replacement_spell_model.name}'.")

        # Perform replacement
        await remove_spell_from_character(db=db, character_id=character.id, spell_id=spell_selection.spell_to_replace_id)
        # Use a simplified CharacterSpellCreate for adding the new one
        replacement_create_schema = CharacterSpellCreate(spell_id=replacement_spell_model.id, is_known=True, is_prepared=False) # Sorcs don't "prepare"
        await add_spell_to_character(db=db, character_id=character.id, spell_association_in=replacement_create_schema)
        print(f"Character {character.name} replaced spell ID {spell_selection.spell_to_replace_id} with {replacement_spell_model.name}")
        # Update pre_selection_known_spell_ids for subsequent logic
        pre_selection_known_spell_ids.remove(spell_selection.spell_to_replace_id)
        pre_selection_known_spell_ids.add(replacement_spell_model.id)


    # --- Handle New Spell Learned (if one is due) ---
    if spell_selection.new_spell_learned_id is not None:
        if spells_to_learn_this_level <= 0 and not (spell_selection.spell_to_replace_id and spell_selection.replacement_spell_id):
             # Only raise if they are not also doing a replacement (replacement doesn't count as a "new spell known" slot from leveling)
             # Or if they already know max spells
            if current_known_spells_count >= num_spells_target_at_new_level:
                 raise ValueError(f"Sorcerer at level {char_level} already knows the maximum of {num_spells_target_at_new_level} spells.")

        new_spell_to_learn_model = await db.get(SpellModel, spell_selection.new_spell_learned_id)
        if not new_spell_to_learn_model:
            raise ValueError(f"Chosen new spell with ID {spell_selection.new_spell_learned_id} not found.")
        if new_spell_to_learn_model.level == 0 or new_spell_to_learn_model.level > max_spell_level_learnable:
            raise ValueError(f"New spell '{new_spell_to_learn_model.name}' is of invalid level ({new_spell_to_learn_model.level}) for a level {char_level} Sorcerer.")
        if not (new_spell_to_learn_model.dnd_classes and "sorcerer" in [c.lower() for c in new_spell_to_learn_model.dnd_classes]):
            raise ValueError(f"New spell '{new_spell_to_learn_model.name}' is not a Sorcerer spell.")
        if new_spell_to_learn_model.id in pre_selection_known_spell_ids:
            raise ValueError(f"Character already knows the new spell '{new_spell_to_learn_model.name}'.")

        new_spell_create_schema = CharacterSpellCreate(spell_id=new_spell_to_learn_model.id, is_known=True, is_prepared=False)
        await add_spell_to_character(db=db, character_id=character.id, spell_association_in=new_spell_create_schema)
        print(f"Character {character.name} learned new spell: {new_spell_to_learn_model.name}")
    
    elif spells_to_learn_this_level > 0: # They should have learned a spell but didn't provide one
        raise ValueError(f"A new spell selection is required. Sorcerers learn {spells_to_learn_this_level} new spell(s) at level {char_level}.")

    # Final validation of total known spells
    await db.commit() # Commit changes from add/remove before final count
    await db.refresh(character) # Refresh to update character.known_spells if it's used by next query

    final_known_spells_q = await db.execute(
        select(func.count(CharacterSpellModel.id))
        .join(SpellModel, CharacterSpellModel.spell_id == SpellModel.id)
        .filter(CharacterSpellModel.character_id == character.id, 
                CharacterSpellModel.is_known == True, 
                SpellModel.level > 0) # Count only spells of level 1+
    )
    final_known_spells_count = final_known_spells_q.scalar_one_or_none() or 0

    if final_known_spells_count != num_spells_target_at_new_level:
        raise ValueError(f"Incorrect final number of spells known ({final_known_spells_count}) for level {char_level} Sorcerer. Expected: {num_spells_target_at_new_level}.")

    # TODO: Handle Cantrip progression separately if needed. Sorcerers gain cantrips at L4 and L10.
    # This function currently focuses on leveled spells known.

    # Transition to next state or clear
    # For now, assuming spell selection might be the last step implemented for Sorcerer level up.
    # Future: could be "pending_features" if they get a class feature choice.
    character.level_up_status = None 
    print(f"Character {character.name} Sorcerer spell selection complete. Level up status: {character.level_up_status}")

    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

# --- Admin Function for setting character progression (as before) ---
async def admin_update_character_progression(
    db: AsyncSession, *, character: CharacterModel, progression_in: AdminCharacterProgressionUpdate
) -> CharacterModel:
    # ... (existing admin_update_character_progression logic) ...
    updated = False
    if progression_in.level is not None:
        max_level = 50 if character.is_ascended_tier else 30
        if not (1 <= progression_in.level <= max_level):
            raise ValueError(f"Admin: Target level ({progression_in.level}) is outside the allowed range (1-{max_level}) for this character's tier.")
        character.level = progression_in.level
        character.experience_points = get_xp_for_level(character.level)
        if character.hit_die_type and character.constitution is not None:
            con_mod = calculate_ability_modifier(character.constitution)
            new_max_hp = character.hit_die_type + con_mod 
            if character.level > 1:
                for _lvl in range(2, character.level + 1):
                    new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
            character.hit_points_max = new_max_hp
            character.hit_points_current = new_max_hp
        character.hit_dice_total = character.level
        character.hit_dice_remaining = character.level
        character.level_up_status = None 
        updated = True
    elif progression_in.experience_points is not None:
        character.experience_points = progression_in.experience_points
        new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
        if new_level != character.level: # Check if level actually changed
            previous_level_for_calc = character.level # Store old level before updating
            character.level = new_level
            character.hit_dice_total = new_level
            character.hit_dice_remaining = new_level # Regain all on level change via XP set by admin
            
            # Recalculate HP based on all levels gained
            if character.hit_die_type and character.constitution is not None:
                con_mod = calculate_ability_modifier(character.constitution)
                # Start with L1 HP
                new_max_hp = character.hit_die_type + con_mod
                # Add HP for subsequent levels up to the new level
                if character.level > 1:
                    for _lvl in range(2, character.level + 1):
                        new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
                character.hit_points_max = new_max_hp
                character.hit_points_current = new_max_hp # Full heal
            character.level_up_status = None # Admin set, clear pending status
        updated = True
    if updated:
        db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)


