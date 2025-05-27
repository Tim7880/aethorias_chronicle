# Path: api/app/schemas/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import schemas from other modules for nesting if needed
from .user import User as UserSchema
from .character import Character as CharacterSchema

# --- Campaign Member Schemas ---

class CampaignMemberBase(BaseModel):
    user_id: int # The ID of the user who is the member (player)
    character_id: Optional[int] = None # The ID of the character they are using

class CampaignMemberCreate(CampaignMemberBase): # Used internally by CRUD if needed
    pass

# NEW Schema for the request body when a DM adds a user to a campaign
class CampaignMemberAdd(BaseModel):
    user_id_to_add: int = Field(..., description="ID of the user to add as a player")
    character_id: Optional[int] = Field(None, description="ID of the character the player will use (optional at time of adding)")

class CampaignMemberUpdateCharacter(BaseModel): # For player to update their character in a campaign
    character_id: Optional[int] = Field(None, description="ID of the new character, or null to unassign")

class CampaignMember(CampaignMemberBase): # For reading campaign member details
    id: int
    campaign_id: int
    joined_at: datetime
    user: Optional[UserSchema] = None # Populate with user details when reading
    character: Optional[CharacterSchema] = None # Populate with character details when reading

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

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None
    house_rules: Optional[str] = None
        
class CampaignInDBBase(CampaignBase):
    id: int
    dm_user_id: int
    created_at: datetime
    updated_at: datetime
        
    class Config:
        from_attributes = True

class Campaign(CampaignInDBBase):
    dm: Optional[UserSchema] = None
    members: List[CampaignMember] = []

    