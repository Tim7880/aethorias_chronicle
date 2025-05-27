# Path: api/app/routers/spells.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.spell import Spell as SpellSchema # Pydantic schema for Spell response
from app.crud import crud_spell # Importing the crud_spell module
from app.models.user import User as UserModel # For current_user dependency
from app.routers.auth import get_current_active_user # For authentication

router = APIRouter(
    prefix="/api/v1/spells", # Using the /api/v1 prefix consistent with other routers
    tags=["Spells"],
    # Listing spells might be public in some apps, but let's keep it authenticated for now.
    dependencies=[Depends(get_current_active_user)] 
)

@router.get("/", response_model=List[SpellSchema])
async def read_spells_list(
    skip: int = 0,
    limit: int = 100, # Default to fetching up to 100 spells
    db: AsyncSession = Depends(get_db)
    # current_user: UserModel = Depends(get_current_active_user) # Already in router dependencies
    ):
    """
    Retrieve a list of all predefined D&D spells available in the system.
    Spells are ordered by level, then by name.
    """
    spells = await crud_spell.get_spells(db=db, skip=skip, limit=limit)
    return spells

@router.get("/{spell_id}", response_model=SpellSchema)
async def read_single_spell(
    spell_id: int, 
    db: AsyncSession = Depends(get_db)
    # current_user: UserModel = Depends(get_current_active_user) # Already in router dependencies
    ):
    """
    Retrieve a specific predefined D&D spell by its ID.
    """
    db_spell = await crud_spell.get_spell_by_id(db, spell_id=spell_id)
    if db_spell is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found")
    return db_spell

# You could also add an endpoint to get spell by name if desired:
# @router.get("/name/{spell_name}", response_model=SpellSchema)
# async def read_spell_by_name_endpoint(
#     spell_name: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     db_spell = await crud_spell.get_spell_by_name(db, name=spell_name)
#     if db_spell is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Spell with name '{spell_name}' not found")
#     return db_spell