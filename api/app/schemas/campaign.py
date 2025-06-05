# Path: api/app/schemas/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import schemas from other modules for nesting
from .user import User as UserSchema 
from .character import Character as CharacterSchema 
from app.models.campaign_member import CampaignMemberStatusEnum

# --- Campaign Basic Info Schema (for nesting in CampaignMember) ---
class CampaignBasicInfoSchema(BaseModel):
    id: int
    title: str
    dm_user_id: int # Still useful to have the ID
    dm: Optional[UserSchema] = None # <--- ADDED: Nested DM details

    class Config:
        from_attributes = True

# --- Campaign Member Schemas ---
class CampaignMemberBase(BaseModel):
    user_id: int 
    character_id: Optional[int] = None
    status: Optional[CampaignMemberStatusEnum] = CampaignMemberStatusEnum.PENDING_APPROVAL

class CampaignMemberCreate(CampaignMemberBase):
    pass

class CampaignMemberAdd(BaseModel): 
    user_id_to_add: int = Field(..., description="ID of the user to add as a player")
    character_id: Optional[int] = Field(None, description="ID of the character the player will use (optional at time of adding)")

class CampaignMemberUpdateCharacter(BaseModel):
    character_id: Optional[int] = Field(None, description="ID of the new character, or null to unassign")

class CampaignMemberUpdateStatus(BaseModel):
    status: CampaignMemberStatusEnum

class CampaignMember(CampaignMemberBase): 
    id: int
    campaign_id: int 
    status: CampaignMemberStatusEnum 
    joined_at: datetime 
    
    user: Optional[UserSchema] = None 
    character: Optional[CharacterSchema] = None 
    campaign: Optional[CampaignBasicInfoSchema] = None 

    class Config:
        from_attributes = True

# --- Campaign Schemas ---
class CampaignBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None 
    house_rules: Optional[str] = None
    is_open_for_recruitment: Optional[bool] = Field(default=False)

class CampaignCreate(CampaignBase):
    pass 

class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None
    house_rules: Optional[str] = None
    is_open_for_recruitment: Optional[bool] = None

class CampaignInDBBase(CampaignBase):
    id: int
    dm_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Campaign(CampaignInDBBase): 
    dm: Optional[UserSchema] = None # This is for the main Campaign object
    members: List[CampaignMember] = []

class PlayerCampaignJoinRequest(BaseModel):
    character_id: Optional[int] = Field(None, description="Optional ID of the character the player proposes to use.")

