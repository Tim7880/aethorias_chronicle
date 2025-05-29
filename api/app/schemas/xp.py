# Path: api/app/schemas/xp.py
from pydantic import BaseModel, Field

class XPAwardRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount of XP to award (must be positive)")


