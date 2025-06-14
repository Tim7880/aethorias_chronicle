# Path: api/app/crud/crud_dnd_class.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.dnd_class import DndClass as DndClassModel, ClassLevel as ClassLevelModel
from app.schemas.dnd_class import DndClassCreate as DndClassCreateSchema

async def get_dnd_class_by_name(db: AsyncSession, *, name: str) -> Optional[DndClassModel]:
    """
    Retrieves a single D&D class by its unique name, including all level data.
    """
    result = await db.execute(
        select(DndClassModel)
        .options(selectinload(DndClassModel.levels))
        .filter(DndClassModel.name == name)
    )
    return result.scalars().first()

# --- START MODIFICATION ---
async def create_dnd_class(db: AsyncSession, *, dnd_class_in: DndClassCreateSchema) -> DndClassModel:
    """
    Creates a new D&D class and all its associated level data in a single transaction.
    """
    # Create the main class object without the levels list
    class_base_data = dnd_class_in.model_dump(exclude={"levels"})
    db_dnd_class = DndClassModel(**class_base_data)

    # Create the ClassLevel objects and associate them with the parent class
    level_models = [
        ClassLevelModel(**level_data.model_dump()) 
        for level_data in dnd_class_in.levels
    ]
    db_dnd_class.levels.extend(level_models)
    
    db.add(db_dnd_class)
    await db.commit()
    # The refresh automatically loads relationships thanks to how we configured them,
    # but calling get_dnd_class_by_name is a surefire way to get the fully loaded object.
    await db.refresh(db_dnd_class)
    
    # Return the fully loaded object to ensure it matches the response schema
    created_class = await get_dnd_class_by_name(db=db, name=db_dnd_class.name)
    if not created_class:
        raise Exception("Could not retrieve created D&D class after saving.")
        
    return created_class
# --- END MODIFICATION ---

async def get_dnd_classes(db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[DndClassModel]:
    """
    Retrieves a list of D&D classes with pagination, including all level data.
    """
    result = await db.execute(
        select(DndClassModel)
        .options(selectinload(DndClassModel.levels))
        .order_by(DndClassModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


