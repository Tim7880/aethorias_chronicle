# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update # delete, update might not be used directly here but good to have
from sqlalchemy.orm import selectinload, joinedload # joinedload can be an alternative to selectinload
from typing import List, Optional

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel # <--- NEW IMPORT for spell validation
from app.models.character_spell import CharacterSpell as CharacterSpellModel # <--- NEW IMPORT

from app.schemas.character import CharacterCreate as CharacterCreateSchema
from app.schemas.character import CharacterUpdate as CharacterUpdateSchema
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema
from app.schemas.item import CharacterItemUpdate as CharacterItemUpdateSchema
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate # <--- NEW IMPORTS

# --- Character Core CRUD ---
async def create_character_for_user(
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int) -> CharacterModel:
    character_data = character_in.model_dump() 
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
            selectinload(CharacterModel.skills) # Eager load skills
            .selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items) # Eager load inventory items
            .selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells) # <--- EAGER LOAD SPELL ASSOCIATIONS
            .selectinload(CharacterSpellModel.spell_definition)  # <--- THEN EAGER LOAD SPELL DEFINITIONS
        )
        .filter(CharacterModel.id == character_id)
    )
    return result.scalars().first()

async def get_characters_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills)
            .selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items)
            .selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells) # <--- EAGER LOAD SPELL ASSOCIATIONS
            .selectinload(CharacterSpellModel.spell_definition)  # <--- THEN EAGER LOAD SPELL DEFINITIONS
        )
        .filter(CharacterModel.user_id == user_id)
        .order_by(CharacterModel.name) # Optional: order characters by name
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_character(
    db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    db.add(character)
    await db.commit()
    await db.refresh(character)
    # Re-fetch with all relationships for a consistent response object
    return await get_character(db, character.id)


async def delete_character(
    db: AsyncSession, character_id: int, user_id: int ) -> Optional[CharacterModel]:
    # Fetch first to return the object, cascade will handle related deletions
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete)
        await db.commit()
        return character_to_delete
    return None

# --- Character Skill Management Functions (existing) ---
async def get_character_skill_association(
    db: AsyncSession, *, character_id: int, skill_id: int) -> Optional[CharacterSkillModel]:
    result = await db.execute(
        select(CharacterSkillModel).filter_by(character_id=character_id, skill_id=skill_id)
    )
    return result.scalars().first()

async def assign_or_update_skill_proficiency_to_character(
    db: AsyncSession, *, character_id: int, skill_id: int, is_proficient: bool) -> CharacterSkillModel:
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
    # Re-fetch with skill_definition for a rich response
    result_with_skill_def = await db.execute(
        select(CharacterSkillModel)
        .options(selectinload(CharacterSkillModel.skill_definition))
        .filter(CharacterSkillModel.id == db_char_skill.id)
    )
    return result_with_skill_def.scalars().first()

async def remove_skill_from_character(
    db: AsyncSession, *, character_id: int, skill_id: int) -> Optional[CharacterSkillModel]:
    # Fetch the association to return it, including the skill_definition
    db_char_skill_to_delete = await db.execute(
        select(CharacterSkillModel)
        .options(selectinload(CharacterSkillModel.skill_definition))
        .filter_by(character_id=character_id, skill_id=skill_id)
    )
    db_char_skill = db_char_skill_to_delete.scalars().first()
    if db_char_skill:
        await db.delete(db_char_skill)
        await db.commit()
        return db_char_skill # Return the object that was deleted
    return None

# --- Character Inventory Item Management Functions (existing) ---
async def get_character_inventory_item(
    db: AsyncSession, *, character_id: int, item_id: int) -> Optional[CharacterItemModel]:
    result = await db.execute(
        select(CharacterItemModel).filter_by(character_id=character_id, item_id=item_id)
    )
    return result.scalars().first()

async def add_item_to_character_inventory(
    db: AsyncSession, *, character_id: int, item_in: CharacterItemCreateSchema) -> CharacterItemModel:
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
        # Return the state before deletion, or None to indicate removal.
        # For consistency, let's return the object that was "logically" removed.
        # The API layer can then decide on 200 with null body or 204.
        # To make it clear it was removed, we'll return None from CRUD.
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
        .options(selectinload(CharacterItemModel.item_definition)) # Eager load for the return
        .filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id)
    )
    db_character_item = result.scalars().first()
    if db_character_item:
        await db.delete(db_character_item)
        await db.commit()
        return db_character_item # Return the object that was deleted
    return None

# --- NEW Character Spell Management Functions ---

async def get_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    """Helper to find if a specific spell is already associated with a character."""
    result = await db.execute(
        select(CharacterSpellModel)
        .filter_by(character_id=character_id, spell_id=spell_id)
    )
    return result.scalars().first()

async def add_spell_to_character(
    db: AsyncSession, *, character_id: int, spell_association_in: CharacterSpellCreate
) -> CharacterSpellModel:
    """Adds a spell to a character's list of known spells."""
    # Verify the spell itself exists
    spell_definition_res = await db.execute(select(SpellModel).filter(SpellModel.id == spell_association_in.spell_id))
    if not spell_definition_res.scalars().first():
        raise ValueError(f"Spell with ID {spell_association_in.spell_id} not found.")

    # Check if this character already knows this spell
    existing_association = await get_character_spell_association(
        db=db, character_id=character_id, spell_id=spell_association_in.spell_id
    )
    if existing_association:
        # Spell is already known. We could update it, or raise an error, or just return it.
        # For now, let's assume if it exists, we don't re-add.
        # If an update is needed (e.g. change 'is_prepared'), use the update endpoint.
        # Let's return the existing one, but ideally the API layer prevents this if it's not an update.
        # Or, we could update its 'is_known' / 'is_prepared' if different.
        # For simplicity, let's stick to "add if not exists". DB constraint handles uniqueness.
        # The API layer should ideally check before calling if the intent is not to update.
        # If this function is called when it exists, it means the DB constraint will likely fire.
        # A cleaner approach is to let the API layer call get_character_spell_association first,
        # or just return existing if that's desired behavior.
        # For now, let's create and let DB unique constraint handle duplicates if API doesn't check.
        # OR, be more robust here:
        raise ValueError(f"Character already knows spell with ID {spell_association_in.spell_id}. Use update endpoint for changes.")


    db_character_spell = CharacterSpellModel(
        character_id=character_id,
        spell_id=spell_association_in.spell_id,
        is_known=spell_association_in.is_known,
        is_prepared=spell_association_in.is_prepared
    )
    db.add(db_character_spell)
    
    try:
        await db.commit()
        await db.refresh(db_character_spell)
    except Exception as e: # Catch potential IntegrityError from UniqueConstraint
        await db.rollback()
        # Check if it was a unique constraint violation
        existing = await get_character_spell_association(db=db, character_id=character_id, spell_id=spell_association_in.spell_id)
        if existing: # If it now exists, it means a concurrent write or it was already there
             # This logic could be complex if we try to "get or create" carefully.
             # For now, let's assume a direct add attempt.
             # A better pattern for "add or update flags" might be needed if that's the intent.
             # If we want to allow re-adding to potentially update flags, then fetch first, then update.
             # The current CharacterSpellCreate implies new association.
            raise ValueError(f"Spell {spell_association_in.spell_id} is already associated with character {character_id} (possibly due to concurrent request or pre-existing).") from e
        raise e # Re-raise other errors

    # Re-fetch with spell_definition for a rich response
    result_with_spell_def = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter(CharacterSpellModel.id == db_character_spell.id)
    )
    return result_with_spell_def.scalars().first()


async def update_character_spell_association(
    db: AsyncSession, 
    *, 
    character_id: int, # For ownership check
    spell_id: int, # To identify the specific spell association for this character
    spell_association_update_in: CharacterSpellUpdate
) -> Optional[CharacterSpellModel]:
    """Updates attributes of a spell association for a character (e.g., is_prepared)."""
    
    # Fetch the specific CharacterSpell association
    # We use character_id and spell_id to find the association, not its direct ID,
    # as the API might be structured as /characters/{char_id}/spells/{spell_id}
    result = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition)) # Eager load for return
        .filter(CharacterSpellModel.character_id == character_id, CharacterSpellModel.spell_id == spell_id)
    )
    db_character_spell = result.scalars().first()

    if not db_character_spell:
        return None # Not found

    update_data = spell_association_update_in.model_dump(exclude_unset=True)
    if not update_data: # No actual updates provided
        return db_character_spell # Return as is

    for field, value in update_data.items():
        setattr(db_character_spell, field, value)
    
    db.add(db_character_spell)
    await db.commit()
    await db.refresh(db_character_spell)
    return db_character_spell


async def remove_spell_from_character(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    """Removes a spell association from a character."""
    # Fetch the association to return it, including the spell_definition
    # This finds the CharacterSpell entry using character_id and spell_id
    db_char_spell_to_delete = await db.execute(
        select(CharacterSpellModel)
        .options(selectinload(CharacterSpellModel.spell_definition))
        .filter_by(character_id=character_id, spell_id=spell_id)
    )
    db_character_spell = db_char_spell_to_delete.scalars().first()

    if db_character_spell:
        await db.delete(db_character_spell)
        await db.commit()
        return db_character_spell # Return the object that was deleted
    return None


