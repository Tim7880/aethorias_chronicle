# Path: api/app/crud/crud_campaign_member.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from fastapi import HTTPException, status
from app.models.campaign_member import CampaignMember as CampaignMemberModel, CampaignMemberStatusEnum
from app.models.campaign import Campaign as CampaignModel
from app.models.user import User as UserModel
from app.models.character import Character as CharacterModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel


async def delete_user_join_request(
    db: AsyncSession, *, campaign_member_id: int, requesting_user_id: int
) -> CampaignMemberModel:
    """
    Deletes a user's own campaign join request.
    It fetches the full object first to return for the response, then deletes.
    """
    # Step 1: Fetch the full object for the response, with all relationships loaded.
    result = await db.execute(
        select(CampaignMemberModel)
        .options(
            selectinload(CampaignMemberModel.user),
            selectinload(CampaignMemberModel.campaign).options(selectinload(CampaignModel.dm)),
            selectinload(CampaignMemberModel.character).options(
                selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
            )
        )
        .filter(CampaignMemberModel.id == campaign_member_id)
    )
    join_request_to_delete = result.scalars().first()


    # Step 2: Validation checks
    if not join_request_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Join request not found."
        )

    if join_request_to_delete.user_id != requesting_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to cancel this join request."
        )

    if join_request_to_delete.status != CampaignMemberStatusEnum.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request cannot be canceled as its status is '{join_request_to_delete.status.value}', not 'pending_approval'."
        )
    
    # Step 3: Delete operation
    await db.delete(join_request_to_delete)
    await db.commit()

    # Step 4: Return the object data we fetched before deleting
    return join_request_to_delete

async def player_leaves_campaign(
    db: AsyncSession, *, campaign_member_id: int, requesting_user_id: int
) -> CampaignMemberModel:
    """
    Deletes a user's own ACTIVE campaign membership.
    """
    result = await db.execute(
        select(CampaignMemberModel)
        .options(
            selectinload(CampaignMemberModel.user),
            selectinload(CampaignMemberModel.campaign).options(selectinload(CampaignModel.dm)),
            selectinload(CampaignMemberModel.character).options(
                selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
                selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
                selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
            )
        )
        .filter(CampaignMemberModel.id == campaign_member_id)
    )
    membership_to_leave = result.scalars().first()

    # Validation Checks
    if not membership_to_leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign membership not found.")

    if membership_to_leave.user_id != requesting_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to leave the campaign for another user.")

    if membership_to_leave.status != CampaignMemberStatusEnum.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only leave campaigns you are an active member of.")
    
    # Delete the membership record
    await db.delete(membership_to_leave)
    await db.commit()

    # Return the data of the object that was just deleted
    return membership_to_leave

