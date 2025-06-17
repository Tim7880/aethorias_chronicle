# Path: api/app/routers/campaign_sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List

from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.campaign import Campaign as CampaignModel
from app.models.campaign_session import CampaignSession
from app.routers.auth import get_current_active_user
from app.crud import crud_campaign_session
from app.schemas.campaign_session import CampaignSession as CampaignSessionSchema
from app.schemas.initiative_entry import InitiativeEntry as InitiativeEntrySchema, InitiativeEntryCreate

router = APIRouter(
    prefix="/sessions",
    tags=["Campaign Sessions"],
    dependencies=[Depends(get_current_active_user)]
)

# Helper dependency to get a campaign and verify DM ownership
async def get_campaign_and_verify_dm(campaign_id: int, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_active_user)) -> CampaignModel:
    campaign = await db.get(CampaignModel, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if campaign.dm_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the Dungeon Master can perform this action.")
    return campaign

@router.post("/start/{campaign_id}", response_model=CampaignSessionSchema, status_code=status.HTTP_201_CREATED)
async def start_new_session(
    campaign: CampaignModel = Depends(get_campaign_and_verify_dm),
    db: AsyncSession = Depends(get_db)
):
    """
    Starts a new game session for a campaign. Only the DM can perform this action.
    """
    try:
        session = await crud_campaign_session.start_session(db, campaign_id=campaign.id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{session_id}/end", response_model=CampaignSessionSchema)
async def end_active_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Ends an active game session. Only the DM of the campaign can perform this action.
    """
    session = await db.get(CampaignSession, session_id, options=[selectinload(CampaignSession.campaign)])
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.campaign.dm_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the Dungeon Master can end this session.")
    
    ended_session = await crud_campaign_session.end_session(db, session_id=session_id)
    return ended_session

@router.post("/{session_id}/initiative", response_model=InitiativeEntrySchema, status_code=status.HTTP_201_CREATED)
async def add_to_initiative(
    session_id: int,
    entry_in: InitiativeEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Adds a character or monster to the initiative order for a session.
    Only the DM of the campaign can perform this action.
    """
    session = await db.get(CampaignSession, session_id, options=[selectinload(CampaignSession.campaign)])
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.campaign.dm_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the Dungeon Master can modify initiative.")
    
    try:
        new_entry = await crud_campaign_session.add_initiative_entry(db, session_id=session_id, entry_in=entry_in)
        return new_entry
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{session_id}/initiative", response_model=List[InitiativeEntrySchema])
async def get_initiative(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Gets the current initiative order for a session."""
    return await crud_campaign_session.get_initiative_order(db, session_id=session_id)

@router.delete("/{session_id}/initiative", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_initiative(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Clears the entire initiative order for a session. Only the DM can do this."""
    session = await db.get(CampaignSession, session_id, options=[selectinload(CampaignSession.campaign)])
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.campaign.dm_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the Dungeon Master can clear initiative.")
    
    await crud_campaign_session.clear_initiative(db, session_id=session_id)
    return

