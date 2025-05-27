# Path: api/app/crud/crud_item.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.item import Item as ItemModel
# Schemas are typically used by routers for request/response,
# but CRUD can sometimes use Create/Update schemas if creating items via API.
# For now, this primarily reads predefined items.
# from app.schemas.item import ItemCreate as ItemCreateSchema 

async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ItemModel]:
    """
    Retrieve a list of all predefined items, with pagination.
    """
    result = await db.execute(
        select(ItemModel)
        .order_by(ItemModel.name) # Order alphabetically by name
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_item_by_name(db: AsyncSession, name: str) -> Optional[ItemModel]:
    """
    Retrieve a single item by its exact name.
    """
    result = await db.execute(select(ItemModel).filter(ItemModel.name == name))
    return result.scalars().first()

async def get_item_by_id(db: AsyncSession, item_id: int) -> Optional[ItemModel]:
    """
    Retrieve a single item by its ID.
    """
    result = await db.execute(select(ItemModel).filter(ItemModel.id == item_id))
    return result.scalars().first()

# Note: Creating new SRD-like items via API might not be a primary user feature,
# as they are predefined. Homebrew items might be a different system later.
# If item creation via API was needed:
# async def create_item(db: AsyncSession, item_in: ItemCreateSchema) -> ItemModel:
#     db_item = ItemModel(**item_in.model_dump())
#     db.add(db_item)
#     await db.commit()
#     await db.refresh(db_item)
#     return db_item


