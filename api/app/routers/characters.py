# Path: api/app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.character import (
    CharacterCreate, CharacterUpdate, Character as CharacterSchema,
    CharacterBase, 
    CharacterHPLevelUpRequest, 
    CharacterHPLevelUpResponse, # <--- IMPORT NEW RESPONSE SCHEMA
    SpendHitDieRequest, RecordDeathSaveRequest
)
from app.schemas.skill import CharacterSkill as CharacterSkillSchema
from app.schemas.skill import CharacterSkillCreate
from app.schemas.item import (
    CharacterItem as CharacterItemSchema, 
    CharacterItemCreate, 
    CharacterItemUpdate
)
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

# ... (create_character, read_characters_for_user, read_character, update_existing_character_endpoint, delete_existing_character)
# ... (skill and inventory management endpoints) ...
# (These existing endpoints remain the same as the last version I provided)

@router.post("/", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character( # ... (existing code)
    character_in: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    return await crud_character.create_character_for_user(
        db=db, character_in=character_in, user_id=current_user.id
    )

@router.get("/", response_model=List[CharacterSchema])
async def read_characters_for_user( # ... (existing code)
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
async def read_character( # ... (existing code)
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this character")
    return db_character

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_existing_character_endpoint( # ... (existing code from your last working version)
    character_id: int,
    character_update_payload: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this character")
    if character_update_payload.is_ascended_tier is not None and \
       character_update_payload.is_ascended_tier != db_character.is_ascended_tier:
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a superuser can change the ascended tier status.")
    current_character_data = CharacterSchema.model_validate(db_character).model_dump()
    update_data_dict = character_update_payload.model_dump(exclude_unset=True)
    final_state_data = current_character_data.copy()
    final_state_data.update(update_data_dict)
    try:
        CharacterBase(**final_state_data) 
    except ValueError as e: 
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    updated_character_orm = await crud_character.update_character(
        db=db, character=db_character, character_in=character_update_payload
    )
    return updated_character_orm

@router.delete("/{character_id}", response_model=CharacterSchema) 
async def delete_existing_character( # ... (existing code)
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    deleted_character = await crud_character.delete_character(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if deleted_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not authorized to delete")
    return deleted_character

@router.post("/{character_id}/skills", response_model=CharacterSkillSchema, status_code=status.HTTP_201_CREATED)
async def assign_skill_to_character_endpoint( # ... (existing code)
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
async def remove_skill_from_character_endpoint( # ... (existing code)
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

@router.post("/{character_id}/inventory", response_model=CharacterItemSchema, status_code=status.HTTP_201_CREATED)
async def add_item_to_inventory( # ... (existing code)
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
async def update_inventory_item( # ... (existing code)
    character_id: int,
    character_item_id: int,
    item_update_in: CharacterItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    updated_item_assoc = await crud_character.update_character_inventory_item(
        db=db, character_item_id=character_item_id, item_in=item_update_in, character_id=character_id 
    )
    if updated_item_assoc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found, not owned, or removed due to quantity.")
    return updated_item_assoc

@router.delete("/{character_id}/inventory/{character_item_id}", response_model=CharacterItemSchema)
async def remove_item_from_inventory( # ... (existing code)
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


# --- MODIFIED/NEW ENDPOINT for Leveling Up HP, Hit Dice, Death Saves ---
@router.post("/{character_id}/level-up/confirm-hp", response_model=CharacterHPLevelUpResponse) # <--- USE NEW RESPONSE SCHEMA
async def confirm_character_hp_on_level_up(
    character_id: int,
    hp_request: CharacterHPLevelUpRequest, # Contains method: "average" or "roll"
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id: # Only owner can confirm level up choices
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")

    if not db_character.has_pending_level_up:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Character does not have a pending level up for HP confirmation.")

    try:
        updated_character, hp_gained = await crud_character.confirm_level_up_hp_increase( # <--- GET TUPLE
            db=db, character=db_character, method=hp_request.method
        )
        return CharacterHPLevelUpResponse( # <--- CONSTRUCT NEW RESPONSE
            character=updated_character, 
            hp_gained=hp_gained,
            level_up_message=f"{updated_character.name} gained {hp_gained} HP upon reaching level {updated_character.level}!"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{character_id}/spend-hit-die", response_model=CharacterSchema)
async def spend_character_hit_die_endpoint(
    character_id: int,
    spend_request: SpendHitDieRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")
    try:
        updated_character = await crud_character.spend_character_hit_die(
            db=db, character=db_character, dice_roll_result=spend_request.dice_roll_result
        )
        return updated_character
    except ValueError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{character_id}/death-saves", response_model=CharacterSchema)
async def record_character_death_save(
    character_id: int,
    save_request: RecordDeathSaveRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id: # Or DM of current campaign
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")

    updated_character = await crud_character.record_death_save(
        db=db, character=db_character, success=save_request.success
    )
    return updated_character

@router.post("/{character_id}/reset-death-saves", response_model=CharacterSchema)
async def reset_character_death_saves_endpoint(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id: # Or DM of current campaign
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")

    updated_character = await crud_character.reset_death_saves(db=db, character=db_character)
    return updated_character


