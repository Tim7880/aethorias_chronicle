# Path: api/app/schemas/campaign_session.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import InitiativeEntry schemas which we will create next
from .initiative_entry import InitiativeEntry

class CampaignSessionBase(BaseModel):
    is_active: bool = True
    map_state: Optional[Dict[str, Any]] = None

class CampaignSessionCreate(CampaignSessionBase):
    campaign_id: int

class CampaignSessionUpdate(CampaignSessionBase):
    pass

class CampaignSession(CampaignSessionBase):
    id: int
    campaign_id: int
    initiative_entries: List[InitiativeEntry] = []

    class Config:
        from_attributes = True
