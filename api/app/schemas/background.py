# Path: api/app/schemas/background.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BackgroundBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    skill_proficiencies: List[str]
    tool_proficiencies: Optional[str] = None
    languages: Optional[str] = None
    equipment: str
    feature: Dict[str, str] # Expects {"name": "Feature Name", "desc": "Feature description."}

class BackgroundCreate(BackgroundBase):
    pass

class Background(BackgroundBase):
    id: int
    
    class Config:
        from_attributes = True

