# Path: api/app/schemas/xp.py
from pydantic import BaseModel, Field
from typing import List

class XPAwardRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount of XP to award (must be positive)")
    # --- MODIFICATION: Added list of character IDs ---
    character_ids: List[int] = Field(..., min_length=1, description="List of character IDs to award XP to.")
    # --- END MODIFICATION ---
