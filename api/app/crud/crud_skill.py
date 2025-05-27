# Path: api/app/crud/crud_skill.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.skill import Skill as SkillModel
# We don't need schemas here if we're just returning model instances for now,
# or if the router will handle schema conversion.
# from app.schemas.skill import SkillCreate as SkillCreateSchema # Only if creating skills via API

async def get_skills(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SkillModel]:
    """
    Retrieve a list of all predefined skills, with pagination.
    """
    result = await db.execute(
        select(SkillModel)
        .order_by(SkillModel.name) # Order alphabetically by name
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_skill_by_name(db: AsyncSession, name: str) -> SkillModel | None:
    """
    Retrieve a single skill by its exact name.
    """
    result = await db.execute(select(SkillModel).filter(SkillModel.name == name))
    return result.scalars().first()

async def get_skill_by_id(db: AsyncSession, skill_id: int) -> SkillModel | None:
    """
    Retrieve a single skill by its ID.
    """
    result = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
    return result.scalars().first()

# Note: Creating new skills via API might not be needed if they are predefined and seeded.
# If it were needed, a create_skill function would look like this:
# async def create_skill(db: AsyncSession, skill_in: SkillCreateSchema) -> SkillModel:
#     db_skill = SkillModel(
#         name=skill_in.name, 
#         ability_modifier_name=skill_in.ability_modifier_name,
#         description=skill_in.description
#     )
#     db.add(db_skill)
#     await db.commit()
#     await db.refresh(db_skill)
#     return db_skill