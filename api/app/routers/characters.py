# Path: api/app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.character import CharacterCreate, CharacterUpdate, Character as CharacterSchema
from app.schemas.skill import CharacterSkill as CharacterSkillSchema
from app.schemas.skill import CharacterSkillCreate
from app.schemas.item import (
    CharacterItem as CharacterItemSchema, 
    CharacterItemCreate, 
    CharacterItemUpdate
)
from app.schemas.character_spell import ( # <--- NEW IMPORTS FOR CHARACTER SPELL SCHEMAS
    CharacterSpell as CharacterSpellSchema,
    CharacterSpellCreate,
    CharacterSpellUpdate
)

from app.crud import crud_character, crud_skill # crud_item is not directly used here, crud_character handles it
# We will use functions from crud_character for spell associations as well.
# from app.crud import crud_spell # For validating spell_id if not done in crud_character

from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/characters", # This prefix is for the main.py include_router
    tags=["Characters"],
    dependencies=[Depends(get_current_active_user)]
)

# --- Character Core Endpoints (existing, response model now includes spells) ---
@router.post("/", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character_endpoint( # Renamed for clarity if create_character is also a CRUD func name
    character_in: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    # The create_character_for_user CRUD now re-fetches with get_character,
    # so it will include empty skills, inventory, and known_spells lists.
    return await crud_character.create_character_for_user(
        db=db, character_in=character_in, user_id=current_user.id
    )

@router.get("/", response_model=List[CharacterSchema])
async def read_characters_for_user_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100):
    characters = await crud_character.get_characters_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    # Will now include known_spells due to schema & CRUD eager loading
    return characters

@router.get("/{character_id}", response_model=CharacterSchema)
async def read_character_endpoint(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this character"
        )
    # Will now include known_spells
    return db_character

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_existing_character_endpoint(
    character_id: int,
    character_in: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character_check = await crud_character.get_character(db=db, character_id=character_id) # Fetch for check first
    if db_character_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character_check.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this character"
        )
    # Pass the fetched character object to update_character CRUD if it expects it,
    # or let crud_character.update_character fetch it again if it prefers just IDs.
    # Our crud_character.update_character expects the model instance.
    updated_character = await crud_character.update_character(
        db=db, character=db_character_check, character_in=character_in
    )
    return updated_character

@router.delete("/{character_id}", response_model=CharacterSchema) 
async def delete_existing_character_endpoint(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    # crud_character.delete_character now fetches the character to return it,
    # and also handles the ownership check if user_id is passed.
    deleted_character = await crud_character.delete_character(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if deleted_character is None: # Means not found or not authorized
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Character not found or not authorized to delete"
        )
    return deleted_character

# --- Character Skill Management Endpoints (existing) ---
@router.post("/{character_id}/skills", response_model=CharacterSkillSchema, status_code=status.HTTP_201_CREATED)
async def assign_skill_to_character_endpoint(
    character_id: int,
    skill_in: CharacterSkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN, 
                            detail="Character not found or not authorized")
    # Validate skill_id (crud_skill.get_skill_by_id is appropriate here if not done in assign_or_update)
    # Our assign_or_update_skill_proficiency_to_character CRUD already validates skill_id.
    try:
        char_skill_association = await crud_character.assign_or_update_skill_proficiency_to_character(
            db=db, character_id=character_id, skill_id=skill_in.skill_id, is_proficient=skill_in.is_proficient
        )
        return char_skill_association
    except ValueError as e: # Catch specific errors from CRUD
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{character_id}/skills/{skill_id}", response_model=CharacterSkillSchema) # Return deleted obj
async def remove_skill_from_character_endpoint(
    character_id: int,
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized")
    
    deleted_assoc = await crud_character.remove_skill_from_character(
        db=db, character_id=character_id, skill_id=skill_id
    )
    if not deleted_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill association not found for this character.")
    return deleted_assoc # Return the deleted skill association object

# --- Character Inventory Item Management Endpoints (existing) ---
@router.post("/{character_id}/inventory", response_model=CharacterItemSchema, status_code=status.HTTP_201_CREATED)
async def add_item_to_inventory_endpoint(
    character_id: int,
    item_in: CharacterItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
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
async def update_inventory_item_endpoint(
    character_id: int,
    character_item_id: int, 
    item_update_in: CharacterItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    # First, verify the character exists and belongs to the user.
    # The CRUD function for update_character_inventory_item also takes character_id for ownership check.
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, # Or 404 if char not found at all
                            detail="Character not found or not authorized for this operation.")

    updated_item_assoc = await crud_character.update_character_inventory_item(
        db=db, 
        character_item_id=character_item_id, 
        item_in=item_update_in,
        character_id=character_id 
    )
    if updated_item_assoc is None:
        # This means item not found for this character OR it was deleted due to quantity <= 0
        # The API could return 204 No Content if it was deleted by quantity.
        # For now, a 404 is a general "it's not there anymore or wasn't to begin with".
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found for this character, or was removed.")
    return updated_item_assoc

@router.delete("/{character_id}/inventory/{character_item_id}", response_model=CharacterItemSchema)
async def remove_item_from_inventory_endpoint(
    character_id: int,
    character_item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    # Verify character ownership first
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized for this operation.")
    
    deleted_item_assoc = await crud_character.remove_item_from_character_inventory(
        db=db, character_item_id=character_item_id, character_id=character_id # CRUD checks ownership again
    )
    if not deleted_item_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found for this character.")
    return deleted_item_assoc

# --- NEW Character Spell Management Endpoints ---

@router.post("/{character_id}/spells", response_model=CharacterSpellSchema, status_code=status.HTTP_201_CREATED)
async def add_spell_to_character_endpoint(
    character_id: int,
    spell_association_in: CharacterSpellCreate, # Contains spell_id, is_known, is_prepared
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Adds a spell to the character's list of known spells.
    """
    # Verify character ownership
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
            detail="Character not found or not authorized"
        )

    try:
        character_spell_association = await crud_character.add_spell_to_character(
            db=db, character_id=character_id, spell_association_in=spell_association_in
        )
        return character_spell_association
    except ValueError as e: # Catch errors from CRUD (e.g., spell not found, or already known)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{character_id}/spells/{spell_id}", response_model=CharacterSpellSchema)
async def update_character_spell_endpoint(
    character_id: int,
    spell_id: int, # ID of the Spell definition
    spell_association_update_in: CharacterSpellUpdate, # Contains is_prepared
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Updates a spell association for a character (e.g., toggles is_prepared).
    Identifies the association using character_id and spell_id.
    """
    # Verify character ownership
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
            detail="Character not found or not authorized"
        )

    updated_association = await crud_character.update_character_spell_association(
        db=db,
        character_id=character_id,
        spell_id=spell_id,
        spell_association_update_in=spell_association_update_in
    )

    if not updated_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell with ID {spell_id} not found in character's known spells, or no update values provided."
        )
    return updated_association


@router.delete("/{character_id}/spells/{spell_id}", response_model=CharacterSpellSchema)
async def remove_spell_from_character_endpoint(
    character_id: int,
    spell_id: int, # ID of the Spell definition to remove from character
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Removes a spell from a character's list of known spells.
    """
    # Verify character ownership
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if not db_character else status.HTTP_403_FORBIDDEN,
            detail="Character not found or not authorized"
        )

    deleted_association = await crud_character.remove_spell_from_character(
        db=db, character_id=character_id, spell_id=spell_id
    )

    if not deleted_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spell with ID {spell_id} not found in character's known spells."
        )
    return deleted_association




