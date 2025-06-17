# Path: api/app/crud/crud_spell.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.spell import Spell as SpellModel
# from app.schemas.spell import SpellCreate as SpellCreateSchema # For if we allowed API creation

async def get_spells(db: AsyncSession, skip: int = 0, limit: int = 1000) -> List[SpellModel]:
    """
    Retrieve a list of all predefined spells, with pagination.
    Orders by spell level, then by name.
    """
    result = await db.execute(
        select(SpellModel)
        .order_by(SpellModel.level, SpellModel.name) # Order by level, then alphabetically
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_spell_by_id(db: AsyncSession, spell_id: int) -> Optional[SpellModel]:
    """
    Retrieve a single spell by its ID.
    """
    result = await db.execute(select(SpellModel).filter(SpellModel.id == spell_id))
    return result.scalars().first()

async def get_spell_by_name(db: AsyncSession, name: str) -> Optional[SpellModel]:
    """
    Retrieve a single spell by its exact name (case-sensitive).
    """
    result = await db.execute(select(SpellModel).filter(SpellModel.name == name))
    return result.scalars().first()

# Note: Creating new SRD-like spells via API might not be a primary user feature,
# as they are predefined. Homebrew spells might be a different system later.
# If spell creation via API was needed:
# async def create_spell(db: AsyncSession, spell_in: SpellCreateSchema) -> SpellModel:
#     db_spell = SpellModel(**spell_in.model_dump())
#     db.add(db_spell)
#     await db.commit()
#     await db.refresh(db_spell)
#     return db_spell



