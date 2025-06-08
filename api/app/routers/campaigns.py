# Path: api/app/routers/campaigns.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # For direct queries if needed
from sqlalchemy.orm import selectinload # For eager loading
from typing import List, Optional

from app.db.database import get_db
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, Campaign as CampaignSchema,
    CampaignMember as CampaignMemberSchema, CampaignMemberAdd, CampaignMemberUpdateCharacter,
    PlayerCampaignJoinRequest, CampaignMemberStatusEnum, CampaignMemberUpdateStatus
)
from app.schemas.character import Character as CharacterSchema # For response of XP award
from app.schemas.xp import XPAwardRequest # <--- NEW IMPORT FOR XP AWARD
from app.crud import crud_campaign, crud_user, crud_character # crud_character for fetching character
from app.models.user import User as UserModel
from app.models.campaign_member import CampaignMember as CampaignMemberModel # For fetching member
from app.routers.auth import get_current_active_user


router = APIRouter(
    prefix="/campaigns", 
    tags=["Campaigns"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/{campaign_id}/award-xp", response_model=List[CharacterSchema])
async def dm_award_xp_to_characters(
    campaign_id: int,
    xp_award: XPAwardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Allows the DM of a campaign to award XP to a list of characters in that campaign.
    """
    # 1. Verify current_user is the DM of this campaign
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can award XP in this campaign."
        )
    
    # 2. Call the CRUD function to handle the logic
    try:
        updated_characters = await crud_campaign.award_xp_to_characters(
            db=db, 
            campaign=campaign, 
            character_ids=xp_award.character_ids, 
            xp_to_add=xp_award.amount
        )
        return updated_characters
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/", response_model=CampaignSchema, status_code=status.HTTP_201_CREATED)
async def create_new_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
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
    if view_as_dm:
        campaigns = await crud_campaign.get_campaigns_by_dm(
            db=db, dm_user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        campaigns = await crud_campaign.get_campaigns_for_user_as_member(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return campaigns

@router.get("/discoverable", response_model=List[CampaignSchema])
async def read_discoverable_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    campaigns = await crud_campaign.get_discoverable_campaigns(db=db, skip=skip, limit=limit)
    return campaigns

@router.get("/{campaign_id}/", response_model=CampaignSchema)
async def read_single_campaign(
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
            detail="Not authorized to access this campaign"
        )
    return campaign

@router.put("/{campaign_id}", response_model=CampaignSchema)
async def update_existing_campaign(
    campaign_id: int,
    campaign_in: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
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

# --- Campaign Member & Join Request Endpoints ---

@router.post("/{campaign_id}/join-requests", response_model=CampaignMemberSchema, status_code=status.HTTP_201_CREATED)
async def player_request_to_join_campaign(
    campaign_id: int,
    join_request_in: PlayerCampaignJoinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    if join_request_in.character_id is not None:
        character = await crud_character.get_character(db=db, character_id=join_request_in.character_id)
        if not character or character.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {join_request_in.character_id} not found or not owned by user."
            )
    join_request_member = await crud_campaign.create_join_request(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
        character_id=join_request_in.character_id
    )
    if not join_request_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not submit join request. Campaign may not exist, not be open for recruitment, you might already be a member/DM, or campaign is full."
        )
    return join_request_member

@router.get("/{campaign_id}/join-requests", response_model=List[CampaignMemberSchema])
async def dm_list_pending_join_requests(
    campaign_id: int,
    skip: int = Query(0, ge=0), # Added skip for pagination
    limit: int = Query(100, ge=1, le=100), # Added limit for pagination
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # The CRUD function get_pending_join_requests_for_campaign now handles DM authorization
    try:
        pending_requests = await crud_campaign.get_pending_join_requests_for_campaign(
            db=db, 
            campaign_id=campaign_id, 
            requesting_user_id=current_user.id, # Pass the current user's ID
            skip=skip,
            limit=limit
        )
        return pending_requests
    except HTTPException as e: # Re-raise HTTPExceptions from CRUD
        raise e
    except Exception as e: # Catch other potential errors
        # Log the error for debugging
        print(f"Error in dm_list_pending_join_requests: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve join requests.")

@router.put("/{campaign_id}/join-requests/{user_id_of_requester}/approve", response_model=CampaignMemberSchema)
async def dm_approve_join_request(
    campaign_id: int,
    user_id_of_requester: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can approve join requests for this campaign."
        )
    active_members_count = sum(1 for member in campaign.members if member.status == CampaignMemberStatusEnum.ACTIVE)
    if campaign.max_players is not None: # Check if max_players is set
        # Check if the requester is already an active member or if approving would exceed max_players
        is_requester_already_active = any(
            member.user_id == user_id_of_requester and member.status == CampaignMemberStatusEnum.ACTIVE 
            for member in campaign.members
        )
        # Only count as exceeding if the requester isn't already active and it would push count over limit
        if not is_requester_already_active and (active_members_count + 1) > campaign.max_players:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campaign is already full or approving this member would exceed maximum player limit.")

    updated_member = await crud_campaign.update_campaign_member_status(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id_of_requester,
        new_status=CampaignMemberStatusEnum.ACTIVE
    )
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Join request for user ID {user_id_of_requester} not found or could not be updated."
        )
    return updated_member

@router.put("/{campaign_id}/join-requests/{user_id_of_requester}/reject", response_model=CampaignMemberSchema)
async def dm_reject_join_request(
    campaign_id: int,
    user_id_of_requester: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can reject join requests for this campaign."
        )
    updated_member = await crud_campaign.update_campaign_member_status(
        db=db,
        campaign_id=campaign_id,
        user_id=user_id_of_requester,
        new_status=CampaignMemberStatusEnum.REJECTED
    )
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Join request for user ID {user_id_of_requester} not found or could not be updated."
        )
    return updated_member

@router.post("/{campaign_id}/members", response_model=CampaignMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_player_to_campaign_by_dm( # Renamed for clarity from generic "add_player_to_campaign"
    campaign_id: int,
    member_in: CampaignMemberAdd, # DM provides user_id_to_add and optional character_id
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can directly add members to this campaign."
        )
    user_to_add = await crud_user.get_user_by_id(db, user_id=member_in.user_id_to_add)
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {member_in.user_id_to_add} not found.")
    
    # DM directly adding a player, typically sets them to ACTIVE.
    # The CRUD function's default for initial_status is ACTIVE.
    new_member = await crud_campaign.add_member_to_campaign(
        db=db, 
        campaign_id=campaign_id, 
        user_id=member_in.user_id_to_add, 
        character_id=member_in.character_id,
        initial_status=CampaignMemberStatusEnum.ACTIVE # Explicitly ACTIVE for DM add
    )
    if not new_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not add member. User may already be a member or campaign may be full.")
    return new_member

@router.get("/{campaign_id}/members", response_model=List[CampaignMemberSchema])
async def list_campaign_members(
    campaign_id: int,
    status: Optional[CampaignMemberStatusEnum] = Query(None, description="Filter members by status (e.g., ACTIVE, PENDING_APPROVAL)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # Authorization: Ensure current_user is DM or an ACTIVE member of this campaign
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    is_active_member = any(m.user_id == current_user.id and m.status == CampaignMemberStatusEnum.ACTIVE for m in campaign.members)
    if campaign.dm_user_id != current_user.id and not is_active_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view members of this campaign."
        )
    
    # If we want to return based on the filter from campaign.members (already eager loaded by get_campaign)
    if status:
        return [member for member in campaign.members if member.status == status]
    return campaign.members # Returns all members if no status filter

@router.delete("/{campaign_id}/members/{user_id_to_remove}", response_model=CampaignMemberSchema)
async def remove_player_from_campaign_by_dm( # Renamed for clarity
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
            detail="Only the DM can remove members from this campaign."
        )
    if campaign.dm_user_id == user_id_to_remove: # DM cannot remove themselves as a player member
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DM cannot be removed as a member via this endpoint.")
    removed_member = await crud_campaign.remove_member_from_campaign(
        db=db, campaign_id=campaign_id, user_id_to_remove=user_id_to_remove
    )
    if not removed_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in this campaign")
    return removed_member

@router.put("/{campaign_id}/me/character", response_model=CampaignMemberSchema)
async def player_updates_character_for_campaign(
    campaign_id: int,
    character_selection: CampaignMemberUpdateCharacter,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    # CRUD function will check if user is a member and update character_id
    # It also re-fetches with eager loading for the response.
    updated_membership = await crud_campaign.update_campaign_member_character(
        db=db, campaign_id=campaign_id, user_id=current_user.id, character_id=character_selection.character_id
    )
    if not updated_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Campaign membership not found for this user, character not owned by user, or character update failed."
        )
    return updated_membership

# --- NEW ENDPOINT for DM to Award XP ---
@router.post("/{campaign_id}/members/{campaign_member_id}/award-xp", response_model=CharacterSchema)
async def dm_award_xp_to_character_in_campaign(
    campaign_id: int,
    campaign_member_id: int, # ID of the CampaignMember record
    xp_award: XPAwardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Allows the DM of a campaign to award XP to a character who is a member of that campaign.
    Updates the character's XP and potentially their level.
    """
    # 1. Verify current_user is the DM of this campaign
    campaign = await crud_campaign.get_campaign(db=db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the DM can award XP in this campaign."
        )

    # 2. Get the CampaignMember record to find the character_id
    # We might need a specific CRUD for this or a direct query
    member_result = await db.execute(
        select(CampaignMemberModel)
        .filter(CampaignMemberModel.id == campaign_member_id, CampaignMemberModel.campaign_id == campaign_id)
    )
    member = member_result.scalars().first()

    if not member or not member.character_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign member not found or no character assigned to this member in this campaign."
        )
    
    # 3. Get the character
    # crud_character.get_character already does eager loading needed for CharacterSchema response
    character_to_award = await crud_character.get_character(db=db, character_id=member.character_id)
    if not character_to_award:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found.")
    
    # 4. Verify the character belongs to the member (user_id on member should match character.user_id)
    if character_to_award.user_id != member.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character does not belong to the specified campaign member."
        )

    # 5. Award XP using the CRUD function
    # The award_xp_to_character CRUD function already re-fetches the character fully.
    try:
        updated_character = await crud_character.award_xp_to_character(
            db=db, character=character_to_award, xp_to_add=xp_award.amount
        )
        return updated_character
    except ValueError as e: # Catch potential ValueError from CRUD (e.g., xp_to_add <= 0)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



