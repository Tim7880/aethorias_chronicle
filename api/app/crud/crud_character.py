# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel # Assuming you have this model

from app.schemas.character import CharacterCreate as CharacterCreateSchema
from app.schemas.character import CharacterUpdate as CharacterUpdateSchema
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema # Used by skill assignment
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema
from app.schemas.item import CharacterItemUpdate as CharacterItemUpdateSchema
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate # Assuming you have these

# --- XP and Leveling Definitions ---
# D&D 5e Standard XP Thresholds for Levels 1-20
XP_THRESHOLDS = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
    9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
    15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
}
# Note: Your CharacterBase schema has level validation up to 30 (or 50 for ascended).
# This XP_THRESHOLDS dict only covers standard 5e progression to 20.
# For levels beyond 20, a different XP progression or direct level setting would be needed.

def get_level_for_xp(xp: int, is_ascended_tier: bool = False) -> int:
    """Determines character level based on XP."""
    # For now, ascended tier doesn't change XP thresholds, only max level.
    # This can be expanded if ascended characters have different XP progression.
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            current_level = level
        else:
            break 
    
    # Ensure level is at least 1, and respects tier-based max if we enforce it here
    # For now, just calculate based on standard XP up to 20.
    # Max level validation is primarily in Pydantic schemas.
    return max(1, current_level)

# --- Character Core CRUD ---
async def create_character_for_user(
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int
) -> CharacterModel:
    character_data = character_in.model_dump() 
    
    # Ensure level is consistent with XP if XP is provided, or default level if XP is 0/None
    # The CharacterBase schema defaults level to 1 and XP to 0.
    # If user provides XP, calculate level. If they provide level but not XP, it might be inconsistent.
    # Pydantic validator on CharacterBase should handle tier-based max level.
    if character_data.get("experience_points") is not None:
        character_data["level"] = get_level_for_xp(
            character_data["experience_points"], 
            character_data.get("is_ascended_tier", False)
        )
    elif character_data.get("level") is None: # If level is not in payload, default to 1
         character_data["level"] = 1
    # If level is in payload but XP is not, the provided level is used.
    # The Pydantic model_validator will check if this level is valid for the tier.

    db_character = CharacterModel(**character_data, user_id=user_id)
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)
    # Re-fetch with all relationships for a consistent response object
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
    
    # If XP is being updated, recalculate and update the level
    if "experience_points" in update_data and update_data["experience_points"] is not None:
        # Determine the tier for level calculation (use current character's tier if not in update_data)
        effective_is_ascended = update_data.get("is_ascended_tier", character.is_ascended_tier)
        new_level_from_xp = get_level_for_xp(update_data["experience_points"], effective_is_ascended)
        
        # Only update level from XP if it's different or if level isn't also being explicitly set
        # to something else in this same update.
        # If 'level' is also in update_data, Pydantic validation on the full object (in router)
        # should ensure consistency based on the final 'is_ascended_tier'.
        # For now, let XP drive the level if XP is provided.
        update_data["level"] = new_level_from_xp

    # Apply all updates
    for field, value in update_data.items():
        setattr(character, field, value)
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    # Re-fetch with all relationships for a consistent response object
    return await get_character(db, character.id)


async def delete_character(
    db: AsyncSession, character_id: int, user_id: int 
) -> Optional[CharacterModel]:
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete) # Cascade should handle skills, items, spells associations
        await db.commit()
        return character_to_delete
    return None

# --- Character Skill Management Functions (existing, ensure they are complete) ---
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
    skill_result = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
    if not skill_result.scalars().first():
        raise ValueError(f"Skill with id {skill_id} not found.") 
    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)
    if db_char_skill:
        db_char_skill.is_proficient = is_proficient
    else:
        db_char_skill = CharacterSkillModel(
            character_id=character_id, skill_id=skill_id, is_proficient=is_proficient
        )
    db.add(db_char_skill)
    await db.commit()
    await db.refresh(db_char_skill)
    result_with_skill_def = await db.execute(
        select(CharacterSkillModel)
        .options(selectinload(CharacterSkillModel.skill_definition))
        .filter(CharacterSkillModel.id == db_char_skill.id)
    )
    return result_with_skill_def.scalars().first()

async def remove_skill_from_character(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    db_char_skill_to_delete = await db.execute(
        select(CharacterSkillModel)
        .options(selectinload(CharacterSkillModel.skill_definition))
        .filter_by(character_id=character_id, skill_id=skill_id)
    )
    db_char_skill = db_char_skill_to_delete.scalars().first()
    if db_char_skill:
        await db.delete(db_char_skill)
        await db.commit()
        return db_char_skill
    return None

# --- Character Inventory Item Management Functions (existing, ensure they are complete) ---
async def get_character_inventory_item(
    db: AsyncSession, *, character_id: int, item_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(
        select(CharacterItemModel).filter_by(character_id=character_id, item_id=item_id)
    )
    return result.scalars().first()

async def add_item_to_character_inventory(
    db: AsyncSession, *, character_id: int, item_in: CharacterItemCreateSchema
) -> CharacterItemModel:
    item_definition_res = await db.execute(select(ItemModel).filter(ItemModel.id == item_in.item_id))
    if not item_definition_res.scalars().first():
        raise ValueError(f"Item with ID {item_in.item_id} not found.")
    db_character_item = await get_character_inventory_item(
        db=db, character_id=character_id, item_id=item_in.item_id
    )
    if db_character_item:
        db_character_item.quantity += item_in.quantity
    else:
        db_character_item = CharacterItemModel(
            character_id=character_id,
            item_id=item_in.item_id,
            quantity=item_in.quantity,
            is_equipped=item_in.is_equipped
        )
    db.add(db_character_item)
    await db.commit()
    await db.refresh(db_character_item)
    result_with_item_def = await db.execute(
        select(CharacterItemModel)
        .options(selectinload(CharacterItemModel.item_definition))
        .filter(CharacterItemModel.id == db_character_item.id)
    )
    return result_with_item_def.scalars().first()

async def update_character_inventory_item(
    db: AsyncSession, *, character_item_id: int, item_in: CharacterItemUpdateSchema, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(
        select(CharacterItemModel)
        .options(selectinload(CharacterItemModel.item_definition))
        .filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id)
    )
    db_character_item = result.scalars().first()
    if not db_character_item:
        return None
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_character_item, field, value)
    if db_character_item.quantity <= 0:
        await db.delete(db_character_item)
        await db.commit()
        return None 
    else:
        db.add(db_character_item)
        await db.commit()
        await db.refresh(db_character_item)
        return db_character_item

async def remove_item_from_character_inventory(
    db: AsyncSession, *, character_item_id: int, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(
        select(CharacterItemModel)
        .options(selectinload(CharacterItemModel.item_definition))
        .filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id)
    )
    db_character_item = result.scalars().first()
    if db_character_item:
        await db.delete(db_character_item)
        await db.commit()
        return db_character_item
    return None

# --- Character Spell Management Functions (ensure these are present from your implementation) ---
async def get_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    result = await db.execute(
        select(CharacterSpellModel).filter_by(character_id=character_id, spell_id=spell_id)
    )
    return result.scalars().first()

async def add_spell_to_character( # Ensure this is your version
    db: AsyncSession, *, character_id: int, spell_association_in: CharacterSpellCreate
) -> CharacterSpellModel:
    spell_definition_res = await db.execute(select(SpellModel).filter(SpellModel.id == spell_association_in.spell_id))
    if not spell_definition_res.scalars().first():
        raise ValueError(f"Spell with ID {spell_association_in.spell_id} not found.")
    
    existing_association = await get_character_spell_association(
        db=db, character_id=character_id, spell_id=spell_association_in.spell_id
    )
    if existing_association:
        raise ValueError(f"Character already knows spell with ID {spell_association_in.spell_id}.")

    db_character_spell = CharacterSpellModel(
        character_id=character_id,
        spell_id=spell_association_in.spell_id,
        is_known=spell_association_in.is_known,
        is_prepared=spell_association_in.is_prepared
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

async def update_character_spell_association( # Ensure this is your version
    db: AsyncSession, *, character_id: int, spell_id: int, spell_association_update_in: CharacterSpellUpdate
) -> Optional[CharacterSpellModel]:
    result = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter(CharacterSpellModel.character_id == character_id, CharacterSpellModel.spell_id == spell_id)
    )
    db_character_spell = result.scalars().first()
    if not db_character_spell: return None
    update_data = spell_association_update_in.model_dump(exclude_unset=True)
    if not update_data: return db_character_spell
    for field, value in update_data.items():
        setattr(db_character_spell, field, value)
    db.add(db_character_spell)
    await db.commit()
    await db.refresh(db_character_spell)
    return db_character_spell

async def remove_spell_from_character( # Ensure this is your version
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

# --- NEW FUNCTION for awarding XP and handling level up ---
async def award_xp_to_character(
    db: AsyncSession, *, character: CharacterModel, xp_to_add: int
) -> CharacterModel:
    """
    Awards XP to a character and updates their level if a new threshold is met.
    """
    if xp_to_add <= 0:
        # It's better to raise an error for invalid input that the API layer can catch
        raise ValueError("XP to award must be a positive integer.")

    current_xp = character.experience_points if character.experience_points is not None else 0
    character.experience_points = current_xp + xp_to_add
    
    new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
    
    if new_level > character.level:
        print(f"Character {character.name} (ID: {character.id}) leveled up from {character.level} to {new_level}!")
        character.level = new_level
        # TODO: Future - Trigger actual level-up process:
        # - HP increase based on class and CON
        # - Flag for ASI choices if applicable at this level
        # - Flag for new spell choices for casters
        # - Granting new class features
        # For now, only the level number is updated.

    db.add(character) # Mark character as dirty for update
    await db.commit()
    await db.refresh(character)
    
    # Re-fetch with all relationships for a consistent response object from the API
    return await get_character(db, character.id)


