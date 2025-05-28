# Path: api/app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.character import (
    CharacterCreate, 
    CharacterUpdate, 
    Character as CharacterSchema,
    CharacterBase # We'll use this for re-validation
)
from app.schemas.skill import CharacterSkill as CharacterSkillSchema
from app.schemas.skill import CharacterSkillCreate
from app.schemas.item import (
    CharacterItem as CharacterItemSchema, 
    CharacterItemCreate, 
    CharacterItemUpdate
)
from app.schemas.character_spell import (
    CharacterSpell as CharacterSpellSchema,
    CharacterSpellCreate,
    CharacterSpellUpdate
)

from app.crud import crud_character, crud_skill
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
    dependencies=[Depends(get_current_active_user)]
)

# --- Character Core Endpoints ---
@router.post("/", response_model=CharacterSchema, status_code=status.HTTP_201_CREATED)
async def create_character_endpoint(
    character_in: CharacterCreate, # CharacterCreate has is_ascended_tier defaulting to False
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    
    # If a non-superuser tries to create a character with is_ascended_tier = True,
    # Pydantic model_validator in CharacterBase would apply ascended limits,
    # but we should also prevent setting it to True on creation by non-superusers.
    # For now, CharacterCreate defaults is_ascended_tier to False.
    # If CharacterCreate allowed is_ascended_tier=True in payload, we'd add a check here:
    # if character_in.is_ascended_tier and not current_user.is_superuser:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only game owner can create ascended characters.")
    # However, since CharacterCreate has is_ascended_tier=False by default from CharacterBase,
    # and it's not explicitly in CharacterCreate's direct fields to be overridden easily by payload
    # unless CharacterBase allows it to be set, this is less of an issue for create.
    # The main control is on UPDATE.

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
    return characters

@router.get("/{character_id}", response_model=CharacterSchema)
async def read_character_endpoint(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if db_character.user_id != current_user.id and not current_user.is_superuser: # Superuser can view any
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this character"
        )
    return db_character

@router.put("/{character_id}", response_model=CharacterSchema)
async def update_existing_character_endpoint(
    character_id: int,
    character_update_payload: CharacterUpdate, # This is the incoming payload
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    # Ownership check for general updates
    if db_character.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this character"
        )

    # --- ASCENDED TIER CHANGE AUTHORIZATION ---
    if character_update_payload.is_ascended_tier is not None and \
       character_update_payload.is_ascended_tier != db_character.is_ascended_tier:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the game owner can change the ascended tier status."
            )
    # --- END AUTHORIZATION ---

    # Create a dictionary of the character's current data
    # The `db_character` is an ORM model. We can convert it to a dict
    # that CharacterBase can understand, or work with its attributes.
    # Pydantic's Character.model_validate(db_character).model_dump() is a safe way.
    character_data_to_validate = CharacterSchema.model_validate(db_character).model_dump()
    
    # Apply updates from the payload. exclude_unset=True means only provided fields are used.
    update_data_dict = character_update_payload.model_dump(exclude_unset=True)
    character_data_to_validate.update(update_data_dict)

    # Now, re-validate the complete "to-be" state using CharacterBase's validator
    # This ensures conditional logic for stats based on the final is_ascended_tier value.
    try:
        validated_data_for_crud = CharacterBase(**character_data_to_validate)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # The validated_data_for_crud now contains all fields (original + updated)
    # and has passed the conditional validation.
    # We pass this complete, validated data to the CRUD function.
    # Note: crud_character.update_character expects a CharacterUpdate schema,
    # but it's safer to pass the individual validated fields or ensure it can handle
    # the full CharacterBase-like structure if we are re-validating this way.
    #
    # Let's refine: crud_character.update_character expects CharacterUpdate.
    # We've done pre-validation. The character_update_payload has already passed
    # its own @model_validator if is_ascended_tier was in it.
    # If is_ascended_tier was NOT in it, but other stats were, the CharacterUpdate
    # validator wouldn't know the original tier.
    #
    # The full object re-validation with CharacterBase is the most robust.
    # If crud_character.update_character takes the ORM object and a CharacterUpdate schema,
    # it will apply partial updates. The key is that the *result* must be valid.

    # Simpler flow if Pydantic CharacterUpdate handles its own context well,
    # OR if CharacterBase validation is the ultimate check.
    # The `character_update_payload` has already been validated by CharacterUpdate's own validator.
    # If that validator is robust enough (e.g., by knowing original tier if needed), we can proceed.
    # My CharacterUpdate validator only did conditional checks if is_ascended_tier WAS in payload.

    # Let's stick to:
    # 1. Auth check for changing is_ascended_tier (done above).
    # 2. Pass the `character_update_payload` (which is a CharacterUpdate instance) to CRUD.
    # The Pydantic @model_validator on CharacterBase (which CharacterCreate and CharacterInDBBase use)
    # will ensure the *final state* is correct upon read, and CharacterCreate for creation.
    # For CharacterUpdate, the @model_validator we added to it will check if `is_ascended_tier` is passed.
    #
    # The most crucial validation is on the *final state*.
    # If CharacterUpdate changes stats, and `is_ascended_tier` is NOT changed,
    # the validator on CharacterUpdate itself doesn't know current tier to apply correct limits.
    # This is why validating the merged state (character_data_to_validate) against CharacterBase
    # is actually very important.

    # So, the validated_data_for_crud (which is a CharacterBase instance) is what we want to save.
    # We need a way for crud_update to apply this.
    # We can create a CharacterUpdate instance from validated_data_for_crud.
    # This ensures all fields that *could* be updated are present.
    
    final_update_schema = CharacterUpdate(**validated_data_for_crud.model_dump())

    updated_character_orm = await crud_character.update_character(
        db=db, character=db_character, character_in=final_update_schema # Pass the validated & complete update data
    )
    return updated_character_orm


@router.delete("/{character_id}", response_model=CharacterSchema) 
async def delete_existing_character_endpoint(
    character_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    deleted_character = await crud_character.delete_character(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if deleted_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Character not found or not authorized to delete"
        )
    return deleted_character

# --- Character Skill Management Endpoints (existing, unchanged) ---
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
    try:
        char_skill_association = await crud_character.assign_or_update_skill_proficiency_to_character(
            db=db, character_id=character_id, skill_id=skill_in.skill_id, is_proficient=skill_in.is_proficient
        )
        return char_skill_association
    except ValueError as e:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{character_id}/skills/{skill_id}", response_model=CharacterSkillSchema)
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
    return deleted_assoc

# --- Character Inventory Item Management Endpoints (existing, unchanged) ---
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
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized for this operation.")

    updated_item_assoc = await crud_character.update_character_inventory_item(
        db=db, 
        character_item_id=character_item_id, 
        item_in=item_update_in,
        character_id=character_id 
    )
    if updated_item_assoc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found for this character, or was removed.")
    return updated_item_assoc

@router.delete("/{character_id}/inventory/{character_item_id}", response_model=CharacterItemSchema)
async def remove_item_from_inventory_endpoint(
    character_id: int,
    character_item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)):
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character or db_character.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Character not found or not authorized for this operation.")
    
    deleted_item_assoc = await crud_character.remove_item_from_character_inventory(
        db=db, character_item_id=character_item_id, character_id=character_id
    )
    if not deleted_item_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found for this character.")
    return deleted_item_assoc

# --- Character Spell Management Endpoints (existing, unchanged) ---
@router.post("/{character_id}/spells", response_model=CharacterSpellSchema, status_code=status.HTTP_201_CREATED)
async def add_spell_to_character_endpoint(
    character_id: int,
    spell_association_in: CharacterSpellCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{character_id}/spells/{spell_id}", response_model=CharacterSpellSchema)
async def update_character_spell_endpoint(
    character_id: int,
    spell_id: int,
    spell_association_update_in: CharacterSpellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
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
    spell_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
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




