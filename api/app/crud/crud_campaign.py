# Path: api/app/crud/crud_campaign.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update # Make sure 'select', 'delete', 'update' are here
from sqlalchemy.orm import selectinload # Make sure 'selectinload' is here
from typing import List, Optional

# Model imports - ensure these paths and aliases are correct
from app.models.campaign import Campaign as CampaignModel
from app.models.campaign_member import CampaignMember as CampaignMemberModel # This is where CampaignMemberModel is defined
from app.models.user import User as UserModel
from app.models.character import Character as CharacterModel

# Schema imports - ensure these paths and aliases are correct
from app.schemas.campaign import CampaignCreate as CampaignCreateSchema
from app.schemas.campaign import CampaignUpdate as CampaignUpdateSchema
# We used CampaignMemberAdd in the router for the request body,
# the CRUD function add_member_to_campaign directly takes user_id, character_id.
# If you had a CampaignMemberCreateSchema used here, ensure it's imported if different from CampaignMemberAdd.

# --- Campaign CRUD Functions ---

async def create_campaign(
    db: AsyncSession, *, campaign_in: CampaignCreateSchema, dm_user_id: int
) -> CampaignModel:
    campaign_data = campaign_in.model_dump()
    db_campaign = CampaignModel(**campaign_data, dm_user_id=dm_user_id)
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign

async def get_campaign(db: AsyncSession, campaign_id: int) -> Optional[CampaignModel]:
    result = await db.execute(
        select(CampaignModel) # Uses 'select'
        .options(
            selectinload(CampaignModel.dm), # Uses 'selectinload'
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.user), # Uses 'CampaignMemberModel'
            selectinload(CampaignModel.members)
            .selectinload(CampaignMemberModel.character) # Uses 'CampaignMemberModel'
        )
        .filter(CampaignModel.id == campaign_id)
    )
    return result.scalars().first()

async def get_campaigns_by_dm(
    db: AsyncSession, *, dm_user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel) # Uses 'select'
        .filter(CampaignModel.dm_user_id == dm_user_id)
        .order_by(CampaignModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_campaigns_for_user_as_member(
    db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel) # Uses 'select'
        .join(CampaignModel.members)
        .filter(CampaignMemberModel.user_id == user_id) # Uses 'CampaignMemberModel'
        .order_by(CampaignModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .distinct()
    )
    return result.scalars().all()

async def update_campaign(
    db: AsyncSession, *, campaign: CampaignModel, campaign_in: CampaignUpdateSchema
) -> CampaignModel:
    update_data = campaign_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

async def delete_campaign(
    db: AsyncSession, *, campaign_id: int, dm_user_id: int
) -> Optional[CampaignModel]:
    result = await db.execute(
        select(CampaignModel).filter(CampaignModel.id == campaign_id, CampaignModel.dm_user_id == dm_user_id) # Uses 'select'
    )
    campaign_to_delete = result.scalars().first()
    if campaign_to_delete:
        await db.delete(campaign_to_delete)
        await db.commit()
        return campaign_to_delete
    return None

# --- Campaign Member CRUD Functions ---

async def add_member_to_campaign(
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int] = None
) -> Optional[CampaignMemberModel]: # Uses 'CampaignMemberModel'
    campaign_result = await db.execute(
        select(CampaignModel).options(selectinload(CampaignModel.members)).filter(CampaignModel.id == campaign_id) # Uses 'select', 'selectinload'
    )
    campaign = campaign_result.scalars().first()

    if not campaign:
        return None 

    existing_member_result = await db.execute(
        select(CampaignMemberModel).filter( # Uses 'select', 'CampaignMemberModel'
            CampaignMemberModel.campaign_id == campaign_id,
            CampaignMemberModel.user_id == user_id
        )
    )
    if existing_member_result.scalars().first():
        return None 

    if campaign.max_players is not None and len(campaign.members) >= campaign.max_players:
        return None 

    if campaign.dm_user_id == user_id:
        return None 

    new_member = CampaignMemberModel( # Uses 'CampaignMemberModel'
        campaign_id=campaign_id,
        user_id=user_id,
        character_id=character_id
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member

async def get_campaign_members(
    db: AsyncSession, *, campaign_id: int
) -> List[CampaignMemberModel]: # Uses 'CampaignMemberModel'
    result = await db.execute(
        select(CampaignMemberModel) # Uses 'select', 'CampaignMemberModel'
        .options(
            selectinload(CampaignMemberModel.user), # Uses 'selectinload', 'CampaignMemberModel'
            selectinload(CampaignMemberModel.character) # Uses 'selectinload', 'CampaignMemberModel'
        )
        .filter(CampaignMemberModel.campaign_id == campaign_id) # Uses 'CampaignMemberModel'
    )
    return result.scalars().all()

async def remove_member_from_campaign(
    db: AsyncSession, *, campaign_id: int, user_id_to_remove: int
) -> Optional[CampaignMemberModel]: # Uses 'CampaignMemberModel'
    result = await db.execute(
        select(CampaignMemberModel).filter( # Uses 'select', 'CampaignMemberModel'
            CampaignMemberModel.campaign_id == campaign_id,
            CampaignMemberModel.user_id == user_id_to_remove
        )
    )
    member_to_delete = result.scalars().first()
    if member_to_delete:
        await db.delete(member_to_delete)
        await db.commit()
        return member_to_delete
    return None

async def update_campaign_member_character(
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int]
) -> Optional[CampaignMemberModel]: # Uses 'CampaignMemberModel'
    result = await db.execute(
        select(CampaignMemberModel).filter( # Uses 'select', 'CampaignMemberModel'
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
        return member_to_update
    return None