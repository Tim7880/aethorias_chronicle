# Path: api/app/schemas/dnd_class.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Pydantic schema for ClassLevel
class ClassLevelBase(BaseModel):
    level: int
    proficiency_bonus: int
    features: Optional[List[Dict[str, Any]]] = None
    spellcasting: Optional[Dict[str, Any]] = None

class ClassLevelCreate(ClassLevelBase):
    pass

class ClassLevel(ClassLevelBase):
    id: int
    dnd_class_id: int

    class Config:
        from_attributes = True

# Pydantic schema for DndClass
class DndClassBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    hit_die: int

# --- MODIFICATION ---
# DndClassCreate now accepts a list of level data.
class DndClassCreate(DndClassBase):
    levels: List[ClassLevelCreate] = Field(..., min_length=1, description="A list of all levels for this class.")
# --- END MODIFICATION ---

class DndClass(DndClassBase):
    id: int
    levels: List[ClassLevel] = []

    class Config:
        from_attributes = True
