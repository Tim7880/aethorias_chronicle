# Path: api/app/routers/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, Campaign as CampaignSchema,
    CampaignMember as CampaignMemberSchema, CampaignMemberAdd, CampaignMemberUpdateCharacter
)
from app.crud import crud_campaign, crud_user 
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user
# For re-fetching CampaignMember with full details if needed
from app.models.campaign_member import CampaignMember as CampaignMemberModel 
from sqlalchemy.orm import selectinload
from sqlalchemy import select

router = APIRouter(
    prefix="/campaigns", # Base prefix for all campaign routes
    tags=["Campaigns"],
    dependencies=[Depends(get_current_active_user)] # All routes here require authentication
)

@router.post("/", response_model=CampaignSchema, status_code=status.HTTP_201_CREATED)
async def create_new_campaign(
    campaign_in: CampaignCreate, # CampaignCreate now includes is_open_for_recruitment (defaults to False)
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new campaign. The creator becomes the DM.
    'is_open_for_recruitment' can be set in the request body (defaults to False).
    """
    return await crud_campaign.create_campaign(
        db=db, campaign_in=campaign_in, dm_user_id=current_user.id
    )

@router.get("/", response_model=List[CampaignSchema])
async def read_user_campaigns(
    view_as_dm: Optional[bool] = False, 
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Retrieve campaigns associated with the current user.
    - If `view_as_dm` is true (e.g., /?view_as_dm=true), lists campaigns where the current user is the DM.
    - Otherwise (default), lists campaigns where the current user is a player member.
    The 'is_open_for_recruitment' status will be included in the response.
    """
    if view_as_dm:
        campaigns = await crud_campaign.get_campaigns_by_dm(
            db=db, dm_user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        campaigns = await crud_campaign.get_campaigns_for_user_as_member(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return campaigns

# --- NEW ENDPOINT for discovering open campaigns ---
@router.get("/discoverable", response_model=List[CampaignSchema])
async def read_discoverable_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    # current_user: UserModel = Depends(get_current_active_user) # Auth is already applied by router
):
    """
    Retrieve a list of campaigns that are marked as open for recruitment.
    """
    campaigns = await crud_campaign.get_discoverable_campaigns(db=db, skip=skip, limit=limit)
    return campaigns
# --- END NEW ENDPOINT ---

@router.get("/{campaign_id}", response_model=CampaignSchema)
async def read_single_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Retrieve a specific campaign by its ID.
    User must be the DM or a member of the campaign.
    The 'is_open_for_recruitment' status will be included.
    """
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id) # Eager loads DM and members
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    is_member = any(member.user_id == current_user.id for member in campaign.members)
    if campaign.dm_user_id != current_user.id and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this campaign"
        )
    return campaign

@router.put("/{campaign_id}", response_model=CampaignSchema)
async def update_existing_campaign(
    campaign_id: int,
    campaign_in: CampaignUpdate, # CampaignUpdate now includes optional is_open_for_recruitment
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update a campaign. Only the DM of the campaign can update it.
    Allows updating 'is_open_for_recruitment'.
    """
    db_campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id) 
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if db_campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this campaign"
        )
    return await crud_campaign.update_campaign(db=db, campaign=db_campaign, campaign_in=campaign_in)

@router.delete("/{campaign_id}", response_model=CampaignSchema)
async def delete_existing_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    deleted_campaign = await crud_campaign.delete_campaign(
        db=db, campaign_id=campaign_id, dm_user_id=current_user.id
    )
    if not deleted_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or not authorized to delete"
        )
    return deleted_campaign

# --- Campaign Member Endpoints (remain the same as before) ---
# ... (POST /{campaign_id}/members, GET /{campaign_id}/members, etc. are unchanged from previous version) ...
# (For brevity, I'm not re-listing them here, but they would be present in your actual file)

@router.post("/{campaign_id}/members", response_model=CampaignMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_player_to_campaign( # ... (existing code) ...
    campaign_id: int,
    member_in: CampaignMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can add members to this campaign"
        )
    user_to_add = await crud_user.get_user_by_id(db, user_id=member_in.user_id_to_add)
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {member_in.user_id_to_add} not found")
    new_member = await crud_campaign.add_member_to_campaign(
        db=db, campaign_id=campaign_id, user_id=member_in.user_id_to_add, character_id=member_in.character_id
    )
    if not new_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not add member. User may already be a member, campaign may be full, or DM cannot be added as player.")
    return new_member


@router.get("/{campaign_id}/members", response_model=List[CampaignMemberSchema])
async def list_campaign_members( # ... (existing code) ...
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    is_member = any(member.user_id == current_user.id for member in campaign.members)
    if campaign.dm_user_id != current_user.id and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view members of this campaign"
        )
    return campaign.members


@router.delete("/{campaign_id}/members/{user_id_to_remove}", response_model=CampaignMemberSchema)
async def remove_player_from_campaign( # ... (existing code) ...
    campaign_id: int,
    user_id_to_remove: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can remove members from this campaign"
        )
    if campaign.dm_user_id == user_id_to_remove:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DM cannot be removed as a member via this endpoint.")
    removed_member = await crud_campaign.remove_member_from_campaign(
        db=db, campaign_id=campaign_id, user_id_to_remove=user_id_to_remove
    )
    if not removed_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in this campaign")
    return removed_member

@router.put("/{campaign_id}/me/character", response_model=CampaignMemberSchema)
async def player_updates_character_for_campaign( # ... (existing code) ...
    campaign_id: int,
    character_selection: CampaignMemberUpdateCharacter,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    updated_membership = await crud_campaign.update_campaign_member_character(
        db=db, campaign_id=campaign_id, user_id=current_user.id, character_id=character_selection.character_id
    )
    if not updated_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Campaign membership not found for this user, or character update failed."
        )
    member_result = await db.execute(
        select(CampaignMemberModel)
        .options(selectinload(CampaignMemberModel.user), selectinload(CampaignMemberModel.character))
        .filter(CampaignMemberModel.id == updated_membership.id)
    )
    fully_loaded_member = member_result.scalars().first()
    if not fully_loaded_member: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to reload campaign member details.")
    return fully_loaded_member



