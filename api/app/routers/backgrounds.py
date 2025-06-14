# Path: api/app/routers/backgrounds.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.background import BackgroundCreate, Background as BackgroundSchema
from app.crud import crud_background
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/backgrounds",
    tags=["Backgrounds"],
    dependencies=[Depends(get_current_active_user)] # All routes require a user to be logged in
)

@router.post("/", response_model=BackgroundSchema, status_code=status.HTTP_201_CREATED, summary="Create a new background (Admin Only)")
async def create_new_background(
    background_in: BackgroundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new D&D background. This endpoint is restricted to superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new background."
        )

    existing_background = await crud_background.get_background_by_name(db=db, name=background_in.name)
    if existing_background:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A background with the name '{background_in.name}' already exists."
        )
    return await crud_background.create_background(db=db, background_in=background_in)


@router.get("/", response_model=List[BackgroundSchema], summary="Get a list of all backgrounds")
async def read_all_backgrounds(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all available backgrounds.
    """
    backgrounds = await crud_background.get_backgrounds(db=db, skip=skip, limit=limit)
    return backgrounds
