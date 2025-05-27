# Path: api/app/routers/skills.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.skill import Skill as SkillSchema
from app.crud import crud_skill
# For now, let's make listing skills an authenticated route for consistency,
# but this could be made public if desired.
from app.models.user import User as UserModel # For current_user dependency
from app.routers.auth import get_current_active_user 

router = APIRouter(
    prefix="/api/v1/skills",
    tags=["Skills"],
    dependencies=[Depends(get_current_active_user)] # All skill routes require authentication for now
)

@router.get("/", response_model=List[SkillSchema])
async def read_skills(
    skip: int = 0,
    limit: int = 100, # Default to fetching up to 100 skills
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all predefined D&D skills.
    """
    skills = await crud_skill.get_skills(db=db, skip=skip, limit=limit)
    return skills

# We could add GET /skills/{skill_id} or /skills/{skill_name} if needed,
# but for now, listing all is probably sufficient as they are predefined.