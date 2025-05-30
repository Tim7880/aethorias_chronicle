# Path: api/app/schemas/admin.py
from pydantic import BaseModel, Field
from typing import Optional

class AdminCharacterProgressionUpdate(BaseModel):
    experience_points: Optional[int] = Field(None, ge=0, description="Set new total XP. Level will be recalculated.")
    level: Optional[int] = Field(None, ge=1, description="Directly set new level. If provided, this takes precedence, and HP/Hit Dice will be reset to this level's base. XP might be set to minimum for this level.")
    # Note: If both level and XP are provided, the 'level' field will dictate the primary change,
    # and XP might be adjusted to the minimum for that level.
    # If only XP is provided, level will be derived.

    