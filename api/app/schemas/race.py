# Path: api/app/schemas/race.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RaceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    ability_score_increase: Dict[str, int]
    size: str
    speed: int
    racial_traits: Optional[List[Dict[str, Any]]] = None
    languages: Optional[str] = None
    subraces: Optional[List[Dict[str, Any]]] = None
class RaceCreate(RaceBase):
    pass

class Race(RaceBase):
    id: int
    
    class Config:
        from_attributes = True

