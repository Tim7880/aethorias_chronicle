# Path: api/app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.character import CharacterCreate, CharacterUpdate, Character as CharacterSchema
from app.schemas.skill import CharacterSkill as CharacterSkillSchema # For response of skill assignment
from app.schemas.skill import CharacterSkillCreate # For request body of skill assignment
from app.crud import crud_character, crud_skill # crud_skill for validating skill_id
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/v1/characters",
    tags=["Characters"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_in: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new character for the currently authenticated user.
    Skill proficiencies should be set via the dedicated /skills sub-resource after creation.
    """
    return await crud_character.create_character_for_user(
        db=db, character_in=character_in, user_id=current_user.id
    )

@router.get("/", response_model=List[CharacterSchema])
async def read_characters_for_user(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all characters belonging to the currently authenticated user.
    Includes skill proficiency information.
    """
    characters = await crud_character.get_characters_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return characters

@router.get("/{character_id}", response_model=CharacterSchema)
async def read_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Retrieve a specific character by its ID.
    Ensures the character belongs to the currently authenticated user.
    Includes skill proficiency information.
    """
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this character"
        )
    return db_character

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_existing_character(
    character_id: int,
    character_in: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update a specific character by its ID.
    Ensures the character belongs to the currently authenticated user.
    Skill proficiencies are managed via the /skills sub-resource.
    """
    db_character = await crud_character.get_character(db=db, character_id=character_id) # Fetches character with skills
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this character"
        )

    updated_character = await crud_character.update_character(
        db=db, character=db_character, character_in=character_in
    )
    return updated_character

@router.delete("/{character_id}", response_model=CharacterSchema) 
async def delete_existing_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    deleted_character = await crud_character.delete_character(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if deleted_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Character not found or not authorized to delete"
        )
    return deleted_character

# --- Character Skill Management Endpoints ---

@router.post("/{character_id}/skills", response_model=CharacterSkillSchema, status_code=status.HTTP_201_CREATED)
async def assign_skill_to_character_endpoint(
    character_id: int,
    skill_in: CharacterSkillCreate, # Expects skill_id and is_proficient
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Assign a skill proficiency to a character or update existing proficiency.
    The character must belong to the current user.
    """
    # Verify character ownership
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or character not found")

    # Verify skill exists (optional, CRUD function also checks but good for early exit)
    skill_def = await crud_skill.get_skill_by_id(db=db, skill_id=skill_in.skill_id)
    if not skill_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill with ID {skill_in.skill_id} not found.")

    try:
        char_skill = await crud_character.assign_or_update_skill_proficiency_to_character(
            db=db,
            character_id=character_id,
            skill_id=skill_in.skill_id,
            is_proficient=skill_in.is_proficient
            # has_expertise=skill_in.has_expertise # If added to schema
        )
        return char_skill
    except ValueError as e: # Catch ValueError from CRUD if skill not found (redundant if checked above)
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{character_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill_from_character_endpoint(
    character_id: int,
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Remove a skill proficiency/association from a character.
    The character must belong to the current user.
    """
    # Verify character ownership
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or character not found")

    deleted = await crud_character.remove_skill_from_character(
        db=db, character_id=character_id, skill_id=skill_id
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill association not found for this character")
    return # No content on successful deletion