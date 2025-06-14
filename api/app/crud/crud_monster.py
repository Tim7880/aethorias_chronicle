# Path: api/app/crud/crud_monster.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.monster import Monster as MonsterModel
from app.schemas.monster import MonsterCreate as MonsterCreateSchema

async def get_monster_by_name(db: AsyncSession, *, name: str) -> Optional[MonsterModel]:
    """
    Retrieves a single monster by its unique name.
    """
    result = await db.execute(select(MonsterModel).filter(MonsterModel.name == name))
    return result.scalars().first()

async def create_monster(db: AsyncSession, *, monster_in: MonsterCreateSchema) -> MonsterModel:
    """
    Creates a new monster in the database.
    """
    # Convert the Pydantic schema to a dictionary
    monster_data = monster_in.model_dump()
    # Create a new SQLAlchemy model instance
    db_monster = MonsterModel(**monster_data)
    # Add the new monster to the session and commit
    db.add(db_monster)
    await db.commit()
    await db.refresh(db_monster)
    return db_monster

async def get_monsters(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[MonsterModel]:
    """
    Retrieves a list of monsters with pagination.
    """
    result = await db.execute(
        select(MonsterModel)
        .order_by(MonsterModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


