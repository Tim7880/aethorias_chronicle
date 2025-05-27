# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update # Ensure delete & update are imported if used elsewhere
from sqlalchemy.orm import selectinload # For eager loading skills
from typing import List, Optional

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel # For type hinting and potentially fetching skill def
from app.models.character_skill import CharacterSkill as CharacterSkillModel # For managing proficiencies
from app.schemas.character import CharacterCreate as CharacterCreateSchema
from app.schemas.character import CharacterUpdate as CharacterUpdateSchema
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema # For creating the association

async def create_character_for_user(
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int
) -> CharacterModel:
    character_data = character_in.model_dump() 

    # Handle proficient_skill_ids if we add it to CharacterCreate schema
    # proficient_skill_ids = character_data.pop("proficient_skill_ids", None) # Example

    db_character = CharacterModel(
        **character_data,
        user_id=user_id
    )
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)

    # If proficient_skill_ids were passed, create CharacterSkill entries
    # if proficient_skill_ids:
    #     for skill_id in proficient_skill_ids:
    #         # Check if skill_id is valid first (optional here, could be API level)
    #         char_skill_in = CharacterSkillCreateSchema(skill_id=skill_id, is_proficient=True)
    #         await assign_skill_to_character(db=db, character_id=db_character.id, character_skill_in=char_skill_in)
    #     await db.refresh(db_character) # Refresh again to load the new skills relationship

    return db_character

async def get_character( # Modified to eager load skills
    db: AsyncSession, character_id: int
) -> Optional[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills) # Eager load the CharacterSkill associations
            .selectinload(CharacterSkillModel.skill_definition) # Then load the actual Skill definition
        )
        .filter(CharacterModel.id == character_id)
    )
    return result.scalars().first()

async def get_characters_by_user( # Modified to eager load skills
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills)
            .selectinload(CharacterSkillModel.skill_definition)
        )
        .filter(CharacterModel.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_character( # No direct skill changes here; handled by dedicated skill endpoints
    db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema
) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return character

async def delete_character(
    db: AsyncSession, character_id: int, user_id: int 
) -> Optional[CharacterModel]:
    # This will also delete associated character_skills due to cascade="all, delete-orphan"
    result = await db.execute(
        select(CharacterModel).filter(CharacterModel.id == character_id, CharacterModel.user_id == user_id)
    )
    character_to_delete = result.scalars().first()

    if character_to_delete:
        await db.delete(character_to_delete)
        await db.commit()
        return character_to_delete
    return None

# --- NEW Character Skill Management Functions ---

async def get_character_skill_association(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    """Gets a specific skill association for a character."""
    result = await db.execute(
        select(CharacterSkillModel).filter_by(character_id=character_id, skill_id=skill_id)
    )
    return result.scalars().first()

async def assign_or_update_skill_proficiency_to_character(
    db: AsyncSession, *, character_id: int, skill_id: int, is_proficient: bool #, has_expertise: Optional[bool] = None
) -> CharacterSkillModel:
    """
    Assigns a skill to a character or updates their proficiency.
    Creates the association if it doesn't exist.
    """
    # Check if the skill itself exists
    skill_result = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
    if not skill_result.scalars().first():
        # In a real app, you might raise an HTTPException here or return None for the router to handle
        raise ValueError(f"Skill with id {skill_id} not found.") 

    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)

    if db_char_skill:
        db_char_skill.is_proficient = is_proficient
        # if has_expertise is not None:
        #     db_char_skill.has_expertise = has_expertise
    else:
        db_char_skill = CharacterSkillModel(
            character_id=character_id,
            skill_id=skill_id,
            is_proficient=is_proficient,
            # has_expertise=has_expertise if has_expertise is not None else False
        )
    db.add(db_char_skill)
    await db.commit()
    await db.refresh(db_char_skill)
    # To return with nested skill_definition for API response:
    result_with_skill = await db.execute(
        select(CharacterSkillModel)
        .options(selectinload(CharacterSkillModel.skill_definition))
        .filter(CharacterSkillModel.id == db_char_skill.id)
    )
    return result_with_skill.scalars().first()


async def remove_skill_from_character(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> bool:
    """
    Removes a skill association (proficiency) from a character.
    Returns True if deleted, False if not found.
    """
    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)
    if db_char_skill:
        await db.delete(db_char_skill)
        await db.commit()
        return True
    return False