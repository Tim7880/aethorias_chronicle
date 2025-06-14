# Path: api/app/routers/monsters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.monster import MonsterCreate, Monster as MonsterSchema, MonsterPublic
from app.crud import crud_monster
from app.models.user import User as UserModel
# --- MODIFICATION: Removed the incorrect import ---
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/monsters",
    tags=["Monsters"],
    dependencies=[Depends(get_current_active_user)] 
)

@router.post("/", response_model=MonsterSchema, status_code=status.HTTP_201_CREATED)
async def create_new_monster(
    monster_in: MonsterCreate,
    db: AsyncSession = Depends(get_db),
    # --- MODIFICATION: Use the standard user dependency ---
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new monster template. (Superuser only)
    """
    # --- MODIFICATION: Added manual superuser check ---
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new monster."
        )

    existing_monster = await crud_monster.get_monster_by_name(db=db, name=monster_in.name)
    if existing_monster:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A monster with the name '{monster_in.name}' already exists."
        )
    return await crud_monster.create_monster(db=db, monster_in=monster_in)


@router.get("/", response_model=List[MonsterPublic])
async def read_all_monsters(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all available monsters with public-safe information.
    """
    monsters = await crud_monster.get_monsters(db=db, skip=skip, limit=limit)
    return monsters
