# Path: api/app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.item import Item as ItemSchema # Pydantic schema for Item response
from app.crud import crud_item # CRUD functions for items
from app.models.user import User as UserModel # For current_user dependency
from app.routers.auth import get_current_active_user # For authentication

router = APIRouter(
    prefix="/api/v1/items",
    tags=["Items"],
    # Listing items might be public in some apps, but for consistency, let's keep it authenticated for now.
    # This can be easily changed by removing the dependency.
    dependencies=[Depends(get_current_active_user)] 
)

@router.get("/", response_model=List[ItemSchema])
async def read_items(
    skip: int = 0,
    limit: int = 100, # Default to fetching up to 100 items
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all predefined D&D items available in the system.
    """
    items = await crud_item.get_items(db=db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific predefined D&D item by its ID.
    """
    db_item = await crud_item.get_item_by_id(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item