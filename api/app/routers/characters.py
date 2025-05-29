# Path: api/app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.character import (
    CharacterCreate, CharacterUpdate, Character as CharacterSchema,
    CharacterBase # Import CharacterBase for re-validation
)
from app.schemas.skill import CharacterSkill as CharacterSkillSchema
from app.schemas.skill import CharacterSkillCreate
from app.schemas.item import (
    CharacterItem as CharacterItemSchema, 
    CharacterItemCreate, 
    CharacterItemUpdate
)
# Assuming you have this for your character spell functionality
from app.schemas.character_spell import CharacterSpell as CharacterSpellSchema, CharacterSpellCreate, CharacterSpellUpdate 
from app.crud import crud_character, crud_skill, crud_item
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel
from sqlalchemy.orm import selectinload
from sqlalchemy import select


router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_in: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # The CharacterCreate schema (which inherits CharacterBase) will have its
    # @model_validator for tier-based stats run by FastAPI automatically.
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
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id and not current_user.is_superuser: # Allow superuser to view
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this character"
        )
    return db_character

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_existing_character_endpoint( # Using your function name
    character_id: int,
    character_update_payload: CharacterUpdate, # Validated by FastAPI against CharacterUpdate schema
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    # Ownership check
    if db_character.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this character"
        )

    # Ascended Tier Change Authorization
    if character_update_payload.is_ascended_tier is not None and \
       character_update_payload.is_ascended_tier != db_character.is_ascended_tier:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a superuser can change the ascended tier status."
            )

    # --- VALIDATE THE FINAL STATE ---
    # 1. Get current character data as a dictionary
    # Use .model_dump() on the Pydantic schema that represents the full character (CharacterSchema)
    # after validating the ORM model instance.
    current_character_data = CharacterSchema.model_validate(db_character).model_dump()
    
    # 2. Get update data from the payload (only fields that were actually sent)
    update_data_dict = character_update_payload.model_dump(exclude_unset=True)
    
    # 3. Create a dictionary representing the "final intended state" after the update
    final_state_data = current_character_data.copy()
    final_state_data.update(update_data_dict) # Apply the changes from the payload

    # 4. Validate this "final intended state" using CharacterBase (which has the tier validator)
    try:
        # CharacterBase expects all its fields or will use defaults.
        # Ensure all necessary fields for CharacterBase are present in final_state_data
        # (e.g., level, xp might be from current_character_data if not in update_data_dict)
        CharacterBase(**final_state_data) # This runs the @model_validator in CharacterBase
    except ValueError as e: # Catch validation errors from CharacterBase's validator
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    # --- END FINAL STATE VALIDATION ---
    
    # If final state validation passes, proceed to update using the original character_update_payload
    # The crud_character.update_character function expects the CharacterUpdate Pydantic model.
    updated_character_orm = await crud_character.update_character(
        db=db, 
        character=db_character,              # The existing SQLAlchemy model instance
        character_in=character_update_payload # The Pydantic schema with *only* the client-sent updates
    )
    return updated_character_orm


@router.delete("/{character_id}", response_model=CharacterSchema) 
async def delete_existing_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # crud_character.delete_character now re-fetches with get_character for response consistency
    deleted_character = await crud_character.delete_character(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if deleted_character is None: # Handles both not found and not owned by current_user (unless superuser)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Character not found or not authorized to delete"
        )
    return deleted_character

# --- Character Skill Management Endpoints ---
# ... (Your existing skill endpoints: POST /{character_id}/skills, DELETE /{character_id}/skills/{skill_id}) ...
@router.post("/{character_id}/skills", response_model=CharacterSkillSchema, status_code=status.HTTP_201_CREATED)
async def assign_skill_to_character_endpoint(
    character_id: int,
    skill_in: CharacterSkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or (db_character.user_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN, 
                            detail="Character not found or not authorized")
    skill_def = await crud_skill.get_skill_by_id(db=db, skill_id=skill_in.skill_id)
    if not skill_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill with ID {skill_in.skill_id} not found.")
    try:
        char_skill_association = await crud_character.assign_or_update_skill_proficiency_to_character(
            db=db, character_id=character_id, skill_id=skill_in.skill_id, is_proficient=skill_in.is_proficient
        )
        return char_skill_association
    except ValueError as e:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{character_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill_from_character_endpoint(
    character_id: int,
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or (db_character.user_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")
    deleted = await crud_character.remove_skill_from_character(
        db=db, character_id=character_id, skill_id=skill_id
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill association not found for this character, or was already removed.")
    return


# --- Character Inventory Item Management Endpoints ---
# ... (Your existing inventory endpoints: POST /{character_id}/inventory, PUT /{character_id}/inventory/{character_item_id}, DELETE /{character_id}/inventory/{character_item_id}) ...
@router.post("/{character_id}/inventory", response_model=CharacterItemSchema, status_code=status.HTTP_201_CREATED)
async def add_item_to_inventory(
    character_id: int,
    item_in: CharacterItemCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or (db_character.user_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")
    try:
        character_item = await crud_character.add_item_to_character_inventory(
            db=db, character_id=character_id, item_in=item_in
        )
        return character_item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{character_id}/inventory/{character_item_id}", response_model=Optional[CharacterItemSchema])
async def update_inventory_item(
    character_id: int,
    character_item_id: int,
    item_update_in: CharacterItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # Ownership of character is checked in the CRUD function via character_id
    updated_item_assoc = await crud_character.update_character_inventory_item(
        db=db, 
        character_item_id=character_item_id, 
        item_in=item_update_in,
        character_id=character_id 
    )
    if updated_item_assoc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found, not owned, or removed due to quantity.")
    return updated_item_assoc

@router.delete("/{character_id}/inventory/{character_item_id}", response_model=CharacterItemSchema)
async def remove_item_from_inventory(
    character_id: int,
    character_item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    deleted_item_assoc = await crud_character.remove_item_from_character_inventory(
        db=db, character_item_id=character_item_id, character_id=character_id
    )
    if not deleted_item_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found or not authorized to delete")
    return deleted_item_assoc

# --- Character Spell Management Endpoints (Assuming you have these) ---
# Example: POST /{character_id}/spells - to add a known/prepared spell
# Example: PUT /{character_id}/spells/{spell_id} - to update prepared status
# Example: DELETE /{character_id}/spells/{spell_id} - to remove a known spell
# These would call your crud_character.add_spell_to_character, update_character_spell_association, remove_spell_from_character


