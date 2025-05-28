# Path: api/app/schemas/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import schemas from other modules for nesting
from .user import User as UserSchema
from .character import Character as CharacterSchema
# We defined CampaignMember specific schemas here, which is good.
# For Skill, we used from .skill import Skill as SkillSchema, etc.

# --- Campaign Member Schemas (remain the same) ---

class CampaignMemberBase(BaseModel):
    user_id: int
    character_id: Optional[int] = None

class CampaignMemberCreate(CampaignMemberBase):
    pass

class CampaignMemberAdd(BaseModel):
    user_id_to_add: int = Field(..., description="ID of the user to add as a player")
    character_id: Optional[int] = Field(None, description="ID of the character the player will use (optional at time of adding)")

class CampaignMemberUpdateCharacter(BaseModel):
    character_id: Optional[int] = Field(None, description="ID of the new character, or null to unassign")

class CampaignMember(CampaignMemberBase):
    id: int
    campaign_id: int
    joined_at: datetime
    user: Optional[UserSchema] = None
    character: Optional[CharacterSchema] = None

    class Config:
        from_attributes = True

# --- Campaign Schemas (Updated) ---

class CampaignBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None 
    house_rules: Optional[str] = None
    is_open_for_recruitment: Optional[bool] = False # <--- NEW FIELD, default to False

class CampaignCreate(CampaignBase):
    # is_open_for_recruitment will default to False from CampaignBase if not provided
    pass 

class CampaignUpdate(BaseModel): # All fields optional for PUT requests
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None
    house_rules: Optional[str] = None
    is_open_for_recruitment: Optional[bool] = None # <--- NEW FIELD, optional for update

class CampaignInDBBase(CampaignBase):
    id: int
    dm_user_id: int
    created_at: datetime
    updated_at: datetime
    # is_open_for_recruitment is inherited from CampaignBase

    class Config:
        from_attributes = True

class Campaign(CampaignInDBBase):
    dm: Optional[UserSchema] = None
    members: List[CampaignMember] = []
    # is_open_for_recruitment is inherited via CampaignInDBBase -> CampaignBase

    