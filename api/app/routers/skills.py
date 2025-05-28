# Path: api/app/routers/skills.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.skill import Skill as SkillSchema
from app.crud import crud_skill
from app.models.user import User as UserModel # For current_user dependency if routes are protected
from app.routers.auth import get_current_active_user # For authentication

router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
    # For now, listing skills will also require authentication for consistency.
    # This could be removed if skills are considered public data.
    dependencies=[Depends(get_current_active_user)] 
)

@router.get("/", response_model=List[SkillSchema])
async def read_skills(
    skip: int = 0,
    limit: int = 100, # Default to fetching up to 100 skills
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all predefined D&D skills available in the system.
    """
    skills = await crud_skill.get_skills(db=db, skip=skip, limit=limit)
    return skills

# Potential future endpoint:
# @router.get("/{skill_id}", response_model=SkillSchema)
# async def read_skill(skill_id: int, db: AsyncSession = Depends(get_db)):
#     db_skill = await crud_skill.get_skill_by_id(db, skill_id=skill_id)
#     if db_skill is None:
#         raise HTTPException(status_code=404, detail="Skill not found")
#     return db_skill





