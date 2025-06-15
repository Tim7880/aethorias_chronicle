# Path: api/app/crud/crud_condition.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.condition import Condition as ConditionModel
from app.schemas.condition import ConditionCreate as ConditionCreateSchema

async def get_condition_by_name(db: AsyncSession, *, name: str) -> Optional[ConditionModel]:
    """
    Retrieves a single condition by its unique name.
    """
    result = await db.execute(select(ConditionModel).filter(ConditionModel.name == name))
    return result.scalars().first()

async def create_condition(db: AsyncSession, *, condition_in: ConditionCreateSchema) -> ConditionModel:
    """
    Creates a new condition in the database.
    """
    condition_data = condition_in.model_dump()
    db_condition = ConditionModel(**condition_data)
    db.add(db_condition)
    await db.commit()
    await db.refresh(db_condition)
    return db_condition

async def get_conditions(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ConditionModel]:
    """
    Retrieves a list of all conditions with pagination.
    """
    result = await db.execute(
        select(ConditionModel)
        .order_by(ConditionModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
