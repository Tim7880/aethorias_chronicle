# Path: api/app/routers/races.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.race import RaceCreate, Race as RaceSchema
from app.crud import crud_race
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/races",
    tags=["Races"],
    dependencies=[Depends(get_current_active_user)] # All race routes require a user to be logged in
)

@router.post("/", response_model=RaceSchema, status_code=status.HTTP_201_CREATED, summary="Create a new race (Admin Only)")
async def create_new_race(
    race_in: RaceCreate,
    db: AsyncSession = Depends(get_db),
    # --- MODIFICATION: Use the standard user dependency ---
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new race template. This endpoint is restricted to superusers.
    """
    # --- MODIFICATION: Added manual superuser check ---
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new race."
        )

    existing_race = await crud_race.get_race_by_name(db=db, name=race_in.name)
    if existing_race:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A race with the name '{race_in.name}' already exists."
        )
    return await crud_race.create_race(db=db, race_in=race_in)


@router.get("/", response_model=List[RaceSchema], summary="Get a list of all races")
async def read_all_races(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all available races.
    """
    races = await crud_race.get_races(db=db, skip=skip, limit=limit)
    return races