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

async def delete_user_join_request(
    db: AsyncSession, *, campaign_member_id: int, requesting_user_id: int
) -> CampaignMemberModel:
    """
    Deletes a user's own campaign join request.

    - Verifies the join request exists.
    - Verifies the user making the request is the one who created it.
    - Verifies the request is still in 'PENDING_APPROVAL' status.
    """
    # Fetch the specific membership record to check its details
    result = await db.execute(
        select(CampaignMemberModel)
        .options(
            selectinload(CampaignMemberModel.campaign).selectinload(CampaignModel.dm),
            selectinload(CampaignMemberModel.user),
            selectinload(CampaignMemberModel.character)
        )
        .filter(CampaignMemberModel.id == campaign_member_id)
    )
    join_request = result.scalars().first()

    # --- VALIDATION CHECKS ---
    if not join_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Join request not found."
        )

    if join_request.user_id != requesting_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to cancel this join request."
        )

    if join_request.status != CampaignMemberStatusEnum.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request cannot be canceled as its status is '{join_request.status.value}', not 'pending_approval'."
        )
    
    # --- DELETE OPERATION ---
    await db.delete(join_request)
    await db.commit()

    # The object still holds the data from before it was deleted, so we can return it
    # for the API response to confirm what was deleted.
    return join_request


