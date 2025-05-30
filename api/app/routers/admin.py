# Path: api/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List # Keep List if other admin endpoints might return lists

from app.db.database import get_db
from app.schemas.character import Character as CharacterSchema # For response
from app.schemas.admin import AdminCharacterProgressionUpdate # Request body schema
from app.crud import crud_character
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user # Base authentication

# --- Dependency to ensure user is a superuser ---
async def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges for this administrative action."
        )
    return current_user

router = APIRouter(
    prefix="/admin", # Base prefix for all admin routes (will be /api/v1/admin later)
    tags=["Admin"],
    dependencies=[Depends(get_current_active_superuser)] # ALL routes in this router require superuser
)

@router.put("/characters/{character_id}/progression", response_model=CharacterSchema)
async def admin_set_character_progression(
    character_id: int,
    progression_in: AdminCharacterProgressionUpdate,
    db: AsyncSession = Depends(get_db)
    # current_superuser is implicitly injected by router dependency but not directly used by name here
):
    """
    Admin endpoint to directly set a character's level and/or experience points.
    Resets HP and Hit Dice according to the new level if level is changed.
    Only accessible by superusers.
    """
    db_character = await crud_character.get_character(db=db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Character with id {character_id} not found")

    try:
        updated_character = await crud_character.admin_update_character_progression(
            db=db, character=db_character, progression_in=progression_in
        )
        return updated_character
    except ValueError as e: # Catch validation errors from CRUD (e.g., level out of range for tier)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Add other admin-specific endpoints here later if needed
# For example:
# - List all users
# - Promote/demote users to/from superuser
# - View/edit any character directly (bypassing ownership)