# Path: api/app/routers/conditions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.condition import ConditionCreate, Condition as ConditionSchema
from app.crud import crud_condition
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/conditions",
    tags=["Conditions"],
    dependencies=[Depends(get_current_active_user)] # All routes require a user to be logged in
)

@router.post("/", response_model=ConditionSchema, status_code=status.HTTP_201_CREATED, summary="Create a new condition (Admin Only)")
async def create_new_condition(
    condition_in: ConditionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new D&D condition. This endpoint is restricted to superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new condition."
        )

    existing_condition = await crud_condition.get_condition_by_name(db=db, name=condition_in.name)
    if existing_condition:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A condition with the name '{condition_in.name}' already exists."
        )
    return await crud_condition.create_condition(db=db, condition_in=condition_in)


@router.get("/", response_model=List[ConditionSchema], summary="Get a list of all conditions")
async def read_all_conditions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all available D&D game conditions.
    """
    conditions = await crud_condition.get_conditions(db=db, skip=skip, limit=limit)
    return conditions
