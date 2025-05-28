# Path: api/app/schemas/campaign.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import schemas from other modules for nesting
from .user import User as UserSchema
from .character import Character as CharacterSchema
from app.models.campaign_member import CampaignMemberStatusEnum # <--- IMPORT THE ENUM

# --- Campaign Member Schemas (Updated) ---

class CampaignMemberBase(BaseModel):
    user_id: int # The ID of the user who is the member (player)
    character_id: Optional[int] = None # The ID of the character they are using
    status: Optional[CampaignMemberStatusEnum] = CampaignMemberStatusEnum.PENDING_APPROVAL # <--- ADDED status field
    # Defaulting to PENDING_APPROVAL here makes sense if this base is used for player join requests.
    # For DM invites, the API endpoint logic might override this default.

class CampaignMemberCreate(CampaignMemberBase): # Used for creating a new membership/request
    # Status will be set by the endpoint logic (e.g. PENDING_APPROVAL for join request, INVITED for DM invite)
    # So, it can be optional here if the logic dictates the initial status.
    # Or, it could be required if the creation always implies a certain status.
    # Let's make it optional here, default from Base will apply if not provided.
    pass

class CampaignMemberAdd(BaseModel): # For DM adding a user directly
    user_id_to_add: int = Field(..., description="ID of the user to add as a player")
    character_id: Optional[int] = Field(None, description="ID of the character the player will use (optional at time of adding)")
    # Status for DM direct add will likely be set to ACTIVE or INVITED by the endpoint logic.

class CampaignMemberUpdateCharacter(BaseModel):
    character_id: Optional[int] = Field(None, description="ID of the new character, or null to unassign")

class CampaignMemberUpdateStatus(BaseModel): # New schema for DM updating status
    status: CampaignMemberStatusEnum # The new status to set

class CampaignMember(CampaignMemberBase): # For reading campaign member details
    id: int
    campaign_id: int
    status: CampaignMemberStatusEnum # Ensure status is included and not optional in response
    joined_at: datetime # This might represent 'request_created_at' or 'status_last_changed_at'
    user: Optional[UserSchema] = None
    character: Optional[CharacterSchema] = None

    class Config:
        from_attributes = True

# --- Campaign Schemas (No changes here from last version) ---

class CampaignBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    banner_image_url: Optional[str] = Field(None, max_length=512)
    max_players: Optional[int] = Field(None, ge=1)
    next_session_utc: Optional[datetime] = None 
    house_rules: Optional[str] = None
    is_open_for_recruitment: Optional[bool] = False

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
    dm: Optional[UserSchema] = None
    members: List[CampaignMember] = [] # This will now list CampaignMember objects with status

# Add this to api/app/schemas/campaign.py
class PlayerCampaignJoinRequest(BaseModel):
    character_id: Optional[int] = Field(None, description="Optional ID of the character the player proposes to use.")
