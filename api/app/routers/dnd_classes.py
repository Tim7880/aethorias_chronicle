# Path: api/app/routers/dnd_classes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.dnd_class import DndClassCreate, DndClass as DndClassSchema
from app.crud import crud_dnd_class
from app.models.user import User as UserModel
# --- MODIFICATION: Removed the incorrect import ---
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/classes",
    tags=["D&D Classes"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=DndClassSchema, status_code=status.HTTP_201_CREATED)
async def create_new_dnd_class(
    dnd_class_in: DndClassCreate,
    db: AsyncSession = Depends(get_db),
    # --- MODIFICATION: Use the standard user dependency ---
    current_user: UserModel = Depends(get_current_active_user) 
):
    """
    Create a new D&D class definition (Superuser only).
    """
    # --- MODIFICATION: Added manual superuser check ---
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a new class."
        )

    existing_class = await crud_dnd_class.get_dnd_class_by_name(db=db, name=dnd_class_in.name)
    if existing_class:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A class with the name '{dnd_class_in.name}' already exists."
        )
    return await crud_dnd_class.create_dnd_class(db=db, dnd_class_in=dnd_class_in)


@router.get("/", response_model=List[DndClassSchema])
async def read_all_dnd_classes(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all available D&D classes.
    """
    dnd_classes = await crud_dnd_class.get_dnd_classes(db=db, skip=skip, limit=limit)
    return dnd_classes

@router.get("/{class_name}", response_model=DndClassSchema)
async def read_single_dnd_class(
    class_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details for a single D&D class by name.
    """
    class_name_formatted = class_name.capitalize()
    db_class = await crud_dnd_class.get_dnd_class_by_name(db=db, name=class_name_formatted)
    if db_class is None:
        raise HTTPException(status_code=404, detail=f"Class '{class_name}' not found")
    return db_class
