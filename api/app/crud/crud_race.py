# Path: api/app/crud/crud_race.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.race import Race as RaceModel
from app.schemas.race import RaceCreate as RaceCreateSchema

async def get_race_by_name(db: AsyncSession, *, name: str) -> Optional[RaceModel]:
    """
    Retrieves a single race by its unique name.
    """
    result = await db.execute(select(RaceModel).filter(RaceModel.name == name))
    return result.scalars().first()

async def create_race(db: AsyncSession, *, race_in: RaceCreateSchema) -> RaceModel:
    """
    Creates a new race in the database.
    """
    race_data = race_in.model_dump()
    db_race = RaceModel(**race_data)
    db.add(db_race)
    await db.commit()
    await db.refresh(db_race)
    return db_race

async def get_races(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[RaceModel]:
    """
    Retrieves a list of all races with pagination.
    """
    result = await db.execute(
        select(RaceModel)
        .order_by(RaceModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

