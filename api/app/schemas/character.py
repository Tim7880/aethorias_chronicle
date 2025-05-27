# Path: api/app/schemas/character.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any 
from datetime import datetime

from .skill import CharacterSkill as CharacterSkillSchema # <--- IMPORT CharacterSkill schema

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    level: Optional[int] = Field(1, ge=1, le=30)
    experience_points: Optional[int] = Field(0, ge=0)
    alignment: Optional[str] = Field(None, max_length=50)
    background_story: Optional[str] = None
    appearance_description: Optional[str] = None

    strength: Optional[int] = Field(10, ge=1, le=30)
    dexterity: Optional[int] = Field(10, ge=1, le=30)
    constitution: Optional[int] = Field(10, ge=1, le=30)
    intelligence: Optional[int] = Field(10, ge=1, le=30)
    wisdom: Optional[int] = Field(10, ge=1, le=30)
    charisma: Optional[int] = Field(10, ge=1, le=30)

    hit_points_current: Optional[int] = None
    hit_points_max: Optional[int] = None
    armor_class: Optional[int] = None

    inventory: Optional[List[Any]] = []

class CharacterCreate(CharacterBase):
    # For MVP, skill proficiencies will be handled via separate endpoints after character creation.
    # Or, if added here, it might be a list of skill_ids to set as proficient.
    # proficient_skill_ids: Optional[List[int]] = None 
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    level: Optional[int] = Field(None, ge=1, le=30)
    experience_points: Optional[int] = Field(None, ge=0)
    alignment: Optional[str] = Field(None, max_length=50)
    background_story: Optional[str] = None
    appearance_description: Optional[str] = None

    strength: Optional[int] = Field(None, ge=1, le=30)
    dexterity: Optional[int] = Field(None, ge=1, le=30)
    constitution: Optional[int] = Field(None, ge=1, le=30)
    intelligence: Optional[int] = Field(None, ge=1, le=30)
    wisdom: Optional[int] = Field(None, ge=1, le=30)
    charisma: Optional[int] = Field(None, ge=1, le=30)

    hit_points_current: Optional[int] = None
    hit_points_max: Optional[int] = None
    armor_class: Optional[int] = None

    inventory: Optional[List[Any]] = None
    # Skill updates will be handled via dedicated endpoints for now.

class CharacterInDBBase(CharacterBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    skills: List[CharacterSkillSchema] = [] # <--- ADDED skills field

    class Config:
        from_attributes = True

class Character(CharacterInDBBase): # This IS our main Character response schema
    pass





