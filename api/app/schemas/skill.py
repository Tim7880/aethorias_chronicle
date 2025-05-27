# Path: api/app/schemas/skill.py
from pydantic import BaseModel, Field
from typing import Optional

# --- Skill Schemas (for the predefined list of D&D skills) ---

class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)
    ability_modifier_name: str = Field(..., max_length=3) # e.g., "DEX", "INT"
    description: Optional[str] = Field(None, max_length=255)

class SkillCreate(SkillBase): # For initially populating the skills table
    pass

class SkillUpdate(SkillBase): # Unlikely to be used by users, more for admin
    name: Optional[str] = Field(None, max_length=100)
    ability_modifier_name: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = Field(None, max_length=255)

class Skill(SkillBase): # For API responses when listing available skills
    id: int

    class Config:
        from_attributes = True

# --- CharacterSkill Schemas (linking Characters to Skills with proficiency) ---

class CharacterSkillBase(BaseModel):
    skill_id: int # The ID of the skill from the 'skills' table
    is_proficient: bool = False
    # has_expertise: Optional[bool] = False # Future enhancement

class CharacterSkillCreate(CharacterSkillBase): # When assigning/updating a skill proficiency for a character
    pass 

class CharacterSkillUpdate(BaseModel): # For updating proficiency/expertise
    is_proficient: Optional[bool] = None
    # has_expertise: Optional[bool] = None

class CharacterSkill(CharacterSkillBase): # For API responses showing a character's skill
    id: int
    # character_id: int # Not usually needed in response if fetched as part of a character
    skill_definition: Skill # <--- RENAMED FROM 'skill' to match SQLAlchemy model relationship
                               # This expects a nested Skill schema with details

    class Config:
        from_attributes = True



