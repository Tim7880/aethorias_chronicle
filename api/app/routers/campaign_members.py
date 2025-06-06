# Path: api/app/routers/campaign_members.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.schemas.campaign import CampaignMember as CampaignMemberSchema
from app.crud import crud_campaign_member
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/campaign-members", # This prefix will apply to all routes in this file
    tags=["Campaign Memberships"],
    dependencies=[Depends(get_current_active_user)]
)

@router.delete("/{campaign_member_id}/my-request", response_model=CampaignMemberSchema)
async def cancel_my_join_request(
    campaign_member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Allows a user to cancel their own PENDING campaign join request.
    """
    try:
        deleted_request = await crud_campaign_member.delete_user_join_request(
            db=db,
            campaign_member_id=campaign_member_id,
            requesting_user_id=current_user.id
        )
        return deleted_request
    except HTTPException as e:
        # Re-raise HTTPException from the CRUD function
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred while canceling join request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while canceling the request."
        )

# Other specific campaign member actions can be added here later,
# such as a player leaving a campaign, or a DM removing a player.


