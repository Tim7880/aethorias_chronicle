# Path: api/app/schemas/skill.py
from pydantic import BaseModel, Field
from typing import Optional, List # Added List for ExpertiseSelectionRequest if it were here

# --- Skill Schemas (for the predefined list of D&D skills) ---

class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)
    ability_modifier_name: str = Field(..., max_length=3) 
    description: Optional[str] = Field(None, max_length=255)

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = Field(None, max_length=100)
    ability_modifier_name: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = Field(None, max_length=255)

class Skill(SkillBase):
    id: int

    class Config:
        from_attributes = True

# --- CharacterSkill Schemas (linking Characters to Skills with proficiency AND EXPERTISE) ---

class CharacterSkillBase(BaseModel):
    skill_id: int 
    is_proficient: bool = False
    has_expertise: bool = False # <--- NEW FIELD, defaults to False

class CharacterSkillCreate(CharacterSkillBase): 
    # When initially assigning a skill, expertise is usually not set here,
    # but via a separate "choose expertise" step.
    # However, having has_expertise here allows the CRUD to set it if needed.
    pass 

class CharacterSkillUpdate(BaseModel): 
    is_proficient: Optional[bool] = None
    has_expertise: Optional[bool] = None # <--- ADDED expertise here for potential updates

class CharacterSkill(CharacterSkillBase): # For API responses showing a character's skill
    id: int 
    skill_definition: Skill 

    class Config:
        from_attributes = True


