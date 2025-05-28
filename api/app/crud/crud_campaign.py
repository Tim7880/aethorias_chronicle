# Path: api/app/crud/crud_campaign.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # delete, update (not actively used by these list functions)
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.campaign import Campaign as CampaignModel
from app.models.campaign_member import CampaignMember as CampaignMemberModel
# from app.models.user import User as UserModel # Not directly used in list functions here
# from app.models.character import Character as CharacterModel # Not directly used in list functions here

from app.schemas.campaign import CampaignCreate as CampaignCreateSchema
from app.schemas.campaign import CampaignUpdate as CampaignUpdateSchema
# CampaignMemberCreateSchema not directly used in this file's current functions

# --- Campaign CRUD Functions ---

async def create_campaign(
    db: AsyncSession, *, campaign_in: CampaignCreateSchema, dm_user_id: int
) -> CampaignModel:
    campaign_data = campaign_in.model_dump() 
    db_campaign_for_creation = CampaignModel(**campaign_data, dm_user_id=dm_user_id)
    db.add(db_campaign_for_creation)
    await db.commit()
    # Re-fetch using get_campaign to ensure all relationships for response model are loaded
    created_campaign = await get_campaign(db=db, campaign_id=db_campaign_for_creation.id)
    if not created_campaign:
        # This should ideally not happen if creation was successful
        raise Exception("Failed to retrieve campaign after creation for response.") 
    return created_campaign

async def get_campaign(db: AsyncSession, campaign_id: int) -> Optional[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), 
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.user), 
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.character)
        )
        .filter(CampaignModel.id == campaign_id)
    )
    return result.scalars().first()

async def get_campaigns_by_dm( # MODIFIED FOR EAGER LOADING
    db: AsyncSession, *, dm_user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), # Eager load DM
            selectinload(CampaignModel.members) # Eager load members list
            .selectinload(CampaignMemberModel.user), # For each member, load user
            selectinload(CampaignModel.members) # Re-specify members for next path
            .selectinload(CampaignMemberModel.character) # For each member, load character
        )
        .filter(CampaignModel.dm_user_id == dm_user_id)
        .order_by(CampaignModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_campaigns_for_user_as_member( # MODIFIED FOR EAGER LOADING
    db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .join(CampaignModel.members) # Join to filter by member
        .options(
            selectinload(CampaignModel.dm), # Eager load DM
            selectinload(CampaignModel.members) # Eager load members list
            .selectinload(CampaignMemberModel.user), # For each member, load user
            selectinload(CampaignModel.members) # Re-specify members for next path
            .selectinload(CampaignMemberModel.character) # For each member, load character
        )
        .filter(CampaignMemberModel.user_id == user_id)
        .order_by(CampaignModel.created_at.desc()) 
        .offset(skip)
        .limit(limit)
        .distinct() 
    )
    return result.scalars().all()

async def get_discoverable_campaigns( # MODIFIED FOR EAGER LOADING
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), # Eager load DM
            selectinload(CampaignModel.members) # Eager load members list (will be empty if no members yet)
            .selectinload(CampaignMemberModel.user),
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.character)
        )
        .filter(CampaignModel.is_open_for_recruitment == True)
        .order_by(CampaignModel.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_campaign( # MODIFIED TO RE-FETCH WITH EAGER LOADING FOR RESPONSE
    db: AsyncSession, *, campaign: CampaignModel, campaign_in: CampaignUpdateSchema
) -> CampaignModel:
    update_data = campaign_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    db.add(campaign)
    await db.commit()
    # Re-fetch the updated campaign with relationships loaded for the response model
    updated_campaign_loaded = await get_campaign(db=db, campaign_id=campaign.id)
    if not updated_campaign_loaded: # Should not happen
        raise Exception("Failed to retrieve campaign after update for response.")
    return updated_campaign_loaded

async def delete_campaign( 
    # ... (delete_campaign logic remains the same, it returns the object before deletion, 
    # or we could change it to return a success message/ID) ...
    # For now, it returns the campaign object, which Pydantic will try to serialize.
    # If the CampaignSchema expects members/dm, this might also need adjustment or pre-loading.
    # However, often for delete, you return minimal info or just a 204.
    # Let's assume for now the client handles the returned object, or we make it return less.
    # The cascade delete on the model should handle members.
    db: AsyncSession, *, campaign_id: int, dm_user_id: int
) -> Optional[CampaignModel]:
    # Fetch with relationships to satisfy response model if it's returned directly
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm),
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.user),
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.character)
        )
        .filter(CampaignModel.id == campaign_id, CampaignModel.dm_user_id == dm_user_id)
    )
    campaign_to_delete = result.scalars().first()
    if campaign_to_delete:
        await db.delete(campaign_to_delete)
        await db.commit()
        return campaign_to_delete # Returning the object before it's fully gone from session state
                                 # or after being expunged might require care.
                                 # Pydantic will try to access its attributes.
    return None


# --- Campaign Member CRUD Functions (remain the same as before) ---
# ... (add_member_to_campaign, get_campaign_members, remove_member_from_campaign, update_campaign_member_character) ...
# Ensure these also return objects with relationships loaded if their response models need them.
# For example, add_member_to_campaign returns CampaignMemberModel, which its schema nests.
# The `get_campaign_members` already does eager loading.
# Let's update `add_member_to_campaign` and `update_campaign_member_character` to ensure they return fully loaded objects for their schemas.

async def add_member_to_campaign(
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int] = None
) -> Optional[CampaignMemberModel]:
    # ... (initial checks remain the same) ...
    campaign_result = await db.execute(
        select(CampaignModel).options(selectinload(CampaignModel.members)).filter(CampaignModel.id == campaign_id)
    )
    campaign = campaign_result.scalars().first()
    if not campaign: return None 
    existing_member_result = await db.execute(select(CampaignMemberModel).filter(CampaignMemberModel.campaign_id == campaign_id, CampaignMemberModel.user_id == user_id))
    if existing_member_result.scalars().first(): return None 
    if campaign.max_players is not None and len(campaign.members) >= campaign.max_players: return None 
    if campaign.dm_user_id == user_id: return None 

    new_member = CampaignMemberModel(campaign_id=campaign_id, user_id=user_id, character_id=character_id)
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member) # Get ID

    # Re-fetch with nested user and character for the response model
    result = await db.execute(
        select(CampaignMemberModel)
        .options(selectinload(CampaignMemberModel.user), selectinload(CampaignMemberModel.character))
        .filter(CampaignMemberModel.id == new_member.id)
    )
    return result.scalars().first()


async def update_campaign_member_character( # Already re-fetches in character router, but good to be consistent if used elsewhere
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int]
) -> Optional[CampaignMemberModel]:
    result = await db.execute(
        select(CampaignMemberModel).filter(
            CampaignMemberModel.campaign_id == campaign_id,
            CampaignMemberModel.user_id == user_id
        )
    )
    member_to_update = result.scalars().first()
    if member_to_update:
        member_to_update.character_id = character_id
        db.add(member_to_update)
        await db.commit()
        await db.refresh(member_to_update)
        # Re-fetch with nested user and character for the response model
        refreshed_result = await db.execute(
            select(CampaignMemberModel)
            .options(selectinload(CampaignMemberModel.user), selectinload(CampaignMemberModel.character))
            .filter(CampaignMemberModel.id == member_to_update.id)
        )
        return refreshed_result.scalars().first()
    return None

