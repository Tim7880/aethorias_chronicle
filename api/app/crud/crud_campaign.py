# Path: api/app/crud/crud_campaign.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, aliased # aliased might be useful for complex queries later
from typing import List, Optional

from fastapi import HTTPException
from app.models.campaign import Campaign as CampaignModel
from app.models.campaign_member import CampaignMember as CampaignMemberModel, CampaignMemberStatusEnum
from app.models.user import User as UserModel
from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel # For skill_definition within CharacterSkill
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel # For item_definition within CharacterItem
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel # For spell_definition within CharacterSpell
from app.models.character_spell import CharacterSpell as CharacterSpellModel # Assuming you have this

from app.schemas.campaign import CampaignCreate as CampaignCreateSchema
from app.schemas.campaign import CampaignUpdate as CampaignUpdateSchema
from app.crud import crud_character

async def award_xp_to_characters(
    db: AsyncSession, *, campaign: CampaignModel, character_ids: List[int], xp_to_add: int
) -> List[CharacterModel]:
    """
    Awards a specified amount of XP to a list of characters within a campaign.
    Verifies that each character is an active member of the campaign.
    """
    if xp_to_add <= 0:
        raise ValueError("XP to award must be a positive number.")

    # Get all active character IDs in the campaign to validate against
    active_member_char_ids = {
        member.character_id for member in campaign.members 
        if member.status == CampaignMemberStatusEnum.ACTIVE and member.character_id is not None
    }

    # Verify that all characters to be awarded are active members
    for char_id in character_ids:
        if char_id not in active_member_char_ids:
            raise ValueError(f"Character with ID {char_id} is not an active member of this campaign.")

    updated_characters = []
    for char_id in character_ids:
        # We can reuse the existing crud_character function
        character_to_award = await crud_character.get_character(db=db, character_id=char_id)
        if character_to_award:
            updated_char = await crud_character.award_xp_to_character(
                db=db, character=character_to_award, xp_to_add=xp_to_add
            )
            updated_characters.append(updated_char)
    
    return updated_characters

# Helper function to consistently load CampaignMember with all details for schemas
async def _get_fully_loaded_campaign_member(db: AsyncSession, campaign_member_id: int) -> Optional[CampaignMemberModel]:
    result = await db.execute(
        select(CampaignMemberModel)
        .options(
            # --- START MODIFICATION ---
            # Eagerly load the campaign and its DM
            selectinload(CampaignMemberModel.campaign).options(
                selectinload(CampaignModel.dm)
            ),
            # Eagerly load the user
            selectinload(CampaignMemberModel.user),
            # Eagerly load the character and all its nested relationships
            selectinload(CampaignMemberModel.character).options(
                selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
            )
            # --- END MODIFICATION ---
        )
        .filter(CampaignMemberModel.id == campaign_member_id)
    )
    return result.scalars().first()

# --- Campaign CRUD Functions ---
async def create_campaign(
    db: AsyncSession, *, campaign_in: CampaignCreateSchema, dm_user_id: int
) -> CampaignModel:
    campaign_data = campaign_in.model_dump() 
    db_campaign_for_creation = CampaignModel(**campaign_data, dm_user_id=dm_user_id)
    db.add(db_campaign_for_creation)
    await db.commit()
    created_campaign = await get_campaign(db=db, campaign_id=db_campaign_for_creation.id)
    if not created_campaign:
        raise Exception("Failed to retrieve campaign after creation for response.") 
    return created_campaign

async def get_campaign(db: AsyncSession, campaign_id: int) -> Optional[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), 
            selectinload(CampaignModel.members).options( # Eager load members AND their nested details
                selectinload(CampaignMemberModel.user),
                selectinload(CampaignMemberModel.campaign),
                selectinload(CampaignMemberModel.character).options(
                    selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                    selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                    selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
                )
            )
        )
        .filter(CampaignModel.id == campaign_id)
    )
    return result.scalars().first()

async def get_campaigns_by_dm(
    db: AsyncSession, *, dm_user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), 
            selectinload(CampaignModel.members).options(
                selectinload(CampaignMemberModel.user),
                selectinload(CampaignMemberModel.character).options(
                    selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                    selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                    selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
                )
            )
        )
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
        select(CampaignModel)
        .join(CampaignModel.members)
        .options(
            selectinload(CampaignModel.dm),
            selectinload(CampaignModel.members).options(
                selectinload(CampaignMemberModel.user),
                selectinload(CampaignMemberModel.character).options(
                    selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                    selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                    selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
                )
            )
        )
        .filter(CampaignMemberModel.user_id == user_id)
        .filter(CampaignMemberModel.status == CampaignMemberStatusEnum.ACTIVE)
        .order_by(CampaignModel.created_at.desc()) 
        .offset(skip)
        .limit(limit)
        .distinct() 
    )
    return result.scalars().all()

async def get_discoverable_campaigns(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[CampaignModel]:
    result = await db.execute(
        select(CampaignModel)
        .options(
            selectinload(CampaignModel.dm), 
            selectinload(CampaignModel.members).options( # Also load members for discoverable campaigns
                selectinload(CampaignMemberModel.user),
                selectinload(CampaignMemberModel.character).options(
                    selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                    selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                    selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
                )
            )
        )
        .filter(CampaignModel.is_open_for_recruitment == True)
        .order_by(CampaignModel.updated_at.desc())
        .offset(skip)
        .limit(limit)
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
    return await get_campaign(db=db, campaign_id=campaign.id) # Re-fetch fully loaded

async def delete_campaign(
    db: AsyncSession, *, campaign_id: int, dm_user_id: int
) -> Optional[CampaignModel]:
    db_campaign = await get_campaign(db=db, campaign_id=campaign_id) # Fetch with relationships
    if not db_campaign or db_campaign.dm_user_id != dm_user_id:
        return None
    await db.delete(db_campaign)
    await db.commit()
    return db_campaign

# --- Campaign Member CRUD Functions ---

async def get_campaign_member_by_user_id(
    db: AsyncSession, *, campaign_id: int, user_id: int
) -> Optional[CampaignMemberModel]:
    # This helper might not need full loading if only used internally for checks
    # But if its result is sometimes returned directly, it would need it.
    # For now, let's assume it's an internal helper.
    result = await db.execute(
        select(CampaignMemberModel).filter_by(campaign_id=campaign_id, user_id=user_id)
    )
    return result.scalars().first()

async def add_member_to_campaign( # DM direct add
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int] = None, 
    initial_status: CampaignMemberStatusEnum = CampaignMemberStatusEnum.ACTIVE
) -> Optional[CampaignMemberModel]:
    # ... (initial checks remain the same: campaign exists, not DM, not already member, not full) ...
    campaign_check = await db.get(CampaignModel, campaign_id)
    if not campaign_check: return None 
    if campaign_check.dm_user_id == user_id: return None 
    existing_member = await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id)
    if existing_member: return None 
    
    campaign_with_members = await get_campaign(db=db, campaign_id=campaign_id) # Check fullness
    active_members_count = sum(1 for m in campaign_with_members.members if m.status == CampaignMemberStatusEnum.ACTIVE)
    if campaign_with_members.max_players is not None and active_members_count >= campaign_with_members.max_players:
        return None

    new_member = CampaignMemberModel(
        campaign_id=campaign_id, user_id=user_id, character_id=character_id, status=initial_status
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return await _get_fully_loaded_campaign_member(db, new_member.id)


async def create_join_request(
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int] = None
) -> Optional[CampaignMemberModel]:
    # ... (initial checks remain the same: campaign open, not DM, not already member, not full) ...
    campaign_check = await db.get(CampaignModel, campaign_id)
    if not campaign_check: return None 
    if not campaign_check.is_open_for_recruitment: return None
    if campaign_check.dm_user_id == user_id: return None 
    existing_member = await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id)
    if existing_member: return None 
    
    campaign_with_members = await get_campaign(db=db, campaign_id=campaign_id)
    active_members_count = sum(1 for m in campaign_with_members.members if m.status == CampaignMemberStatusEnum.ACTIVE)
    if campaign_with_members.max_players is not None and active_members_count >= campaign_with_members.max_players:
        return None

    join_request = CampaignMemberModel(
        campaign_id=campaign_id, user_id=user_id, character_id=character_id, status=CampaignMemberStatusEnum.PENDING_APPROVAL
    )
    db.add(join_request)
    await db.commit()
    await db.refresh(join_request)
    return await _get_fully_loaded_campaign_member(db, join_request.id)

async def get_pending_join_requests_for_campaign(
    db: AsyncSession, *, campaign_id: int, requesting_user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignMemberModel]:
    """
    Retrieves pending join requests for a specific campaign,
    ensuring the requesting user is the DM of the campaign.
    Eagerly loads user, campaign, and character details for each request.
    """
    campaign = await db.get(CampaignModel, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.dm_user_id != requesting_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view join requests for this campaign")

    result = await db.execute(
        select(CampaignMemberModel)
        .options(
            selectinload(CampaignMemberModel.user),
            selectinload(CampaignMemberModel.campaign).options( # Eagerly load the parent campaign
                selectinload(CampaignModel.dm) # And its DM
            ),
            selectinload(CampaignMemberModel.character).options(
                selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
            )
        )
        .filter(CampaignMemberModel.campaign_id == campaign_id)
        .filter(CampaignMemberModel.status == CampaignMemberStatusEnum.PENDING_APPROVAL)
        .order_by(CampaignMemberModel.joined_at.asc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_campaign_member_status(
    db: AsyncSession, *, campaign_id: int, user_id: int, new_status: CampaignMemberStatusEnum
) -> Optional[CampaignMemberModel]:
    member_to_update = await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id)
    if not member_to_update: return None
    member_to_update.status = new_status
    db.add(member_to_update)
    await db.commit()
    await db.refresh(member_to_update)
    return await _get_fully_loaded_campaign_member(db, member_to_update.id)

async def get_campaign_members( # MODIFIED FOR EAGER LOADING
    db: AsyncSession, *, campaign_id: int, status_filter: Optional[CampaignMemberStatusEnum] = None
) -> List[CampaignMemberModel]:
    query = select(CampaignMemberModel).options(
        selectinload(CampaignMemberModel.user),
         # --- ADDED EAGER LOADING FOR CAMPAIGN ---
            selectinload(CampaignMemberModel.campaign).options(
                selectinload(CampaignModel.dm)
            ),
            # --- END ADDITION ---
        selectinload(CampaignMemberModel.character).options(
            selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
        )
    ).filter(CampaignMemberModel.campaign_id == campaign_id)

    if status_filter:
        query = query.filter(CampaignMemberModel.status == status_filter)
    
    result = await db.execute(query)
    return result.scalars().all()

async def remove_member_from_campaign(
    db: AsyncSession, *, campaign_id: int, user_id_to_remove: int
) -> Optional[CampaignMemberModel]:
    # Fetch the full member details *before* deleting for the response
    member_for_return = await _get_fully_loaded_campaign_member(
        db, 
        (await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id_to_remove)).id # Get ID first
        if (await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id_to_remove)) else None
    )
    if not member_for_return: # If it doesn't exist, nothing to delete or return
        return None

    # Now perform the delete operation on the original unfetched or simply fetched member
    # This assumes get_campaign_member_by_user_id doesn't detach or that we re-fetch for delete
    member_to_delete = await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id_to_remove)
    if member_to_delete:
        await db.delete(member_to_delete)
        await db.commit()
        return member_for_return # Return the data of the member that was deleted (with its loaded relationships)
    return None


async def update_campaign_member_character(
    db: AsyncSession, *, campaign_id: int, user_id: int, character_id: Optional[int]
) -> Optional[CampaignMemberModel]:
    member_to_update = await get_campaign_member_by_user_id(db=db, campaign_id=campaign_id, user_id=user_id)
    if not member_to_update: return None
    
    # Add validation here: ensure character_id (if not None) belongs to user_id
    if character_id is not None:
        char_result = await db.execute(select(CharacterModel).filter_by(id=character_id, user_id=user_id))
        if not char_result.scalars().first():
            raise ValueError("Invalid character_id: does not exist or does not belong to the user.")

    member_to_update.character_id = character_id
    db.add(member_to_update)
    await db.commit()
    await db.refresh(member_to_update)
    return await _get_fully_loaded_campaign_member(db, member_to_update.id)

