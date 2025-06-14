# Path: api/app/crud/crud_background.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.background import Background as BackgroundModel
from app.schemas.background import BackgroundCreate as BackgroundCreateSchema

async def get_background_by_name(db: AsyncSession, *, name: str) -> Optional[BackgroundModel]:
    """
    Retrieves a single background by its unique name.
    """
    result = await db.execute(select(BackgroundModel).filter(BackgroundModel.name == name))
    return result.scalars().first()

async def create_background(db: AsyncSession, *, background_in: BackgroundCreateSchema) -> BackgroundModel:
    """
    Creates a new background in the database.
    """
    background_data = background_in.model_dump()
    db_background = BackgroundModel(**background_data)
    db.add(db_background)
    await db.commit()
    await db.refresh(db_background)
    return db_background

async def get_backgrounds(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[BackgroundModel]:
    """
    Retrieves a list of all backgrounds with pagination.
    """
    result = await db.execute(
        select(BackgroundModel)
        .order_by(BackgroundModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
