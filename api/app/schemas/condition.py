# Path: api/app/schemas/condition.py
from pydantic import BaseModel, Field
from typing import Optional

class ConditionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str

class ConditionCreate(ConditionBase):
    pass

class Condition(ConditionBase):
    id: int
    
    class Config:
        from_attributes = True

