# Path: api/app/crud/crud_campaign_session.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.campaign_session import CampaignSession
from app.models.initiative_entry import InitiativeEntry
from app.schemas.initiative_entry import InitiativeEntryCreate

async def get_active_session_for_campaign(db: AsyncSession, campaign_id: int) -> Optional[CampaignSession]:
    """Fetches the currently active session for a given campaign, if one exists."""
    result = await db.execute(
        select(CampaignSession)
        .options(selectinload(CampaignSession.initiative_entries).selectinload(InitiativeEntry.character))
        .filter(CampaignSession.campaign_id == campaign_id, CampaignSession.is_active == True)
    )
    return result.scalars().first()

async def start_session(db: AsyncSession, campaign_id: int) -> CampaignSession:
    """Starts a new session for a campaign, ensuring no other session is active."""
    active_session = await get_active_session_for_campaign(db, campaign_id)
    if active_session:
        raise ValueError("An active session for this campaign already exists.")
    
    new_session = CampaignSession(campaign_id=campaign_id, is_active=True, map_state={})
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    result = await db.execute(
        select(CampaignSession)
        .options(selectinload(CampaignSession.initiative_entries))
        .filter(CampaignSession.id == new_session.id)
    )
    session_with_relations = result.scalars().one()
    return session_with_relations

async def end_session(db: AsyncSession, session_id: int) -> Optional[CampaignSession]:
    """Ends a specific session by setting its is_active flag to False."""
    session = await db.get(CampaignSession, session_id)
    if session:
        session.is_active = False
        db.add(session)
        await db.commit()
        await db.refresh(session)
    return session

async def add_initiative_entry(db: AsyncSession, session_id: int, entry_in: InitiativeEntryCreate) -> InitiativeEntry:
    """Adds a new combatant to the initiative order for a session."""
    session = await db.get(CampaignSession, session_id)
    if not session or not session.is_active:
        raise ValueError("No active session found to add initiative to.")

    new_entry = InitiativeEntry(**entry_in.model_dump(), session_id=session_id)
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

async def get_initiative_order(db: AsyncSession, session_id: int) -> List[InitiativeEntry]:
    """Gets the full initiative order for a session, sorted by roll."""
    result = await db.execute(
        select(InitiativeEntry)
        .options(selectinload(InitiativeEntry.character))
        .filter(InitiativeEntry.session_id == session_id)
        .order_by(InitiativeEntry.initiative_roll.desc())
    )
    return result.scalars().all()

async def clear_initiative(db: AsyncSession, session_id: int):
    """Deletes all initiative entries for a given session."""
    session = await db.get(CampaignSession, session_id, options=[selectinload(CampaignSession.initiative_entries)])
    if not session:
        raise ValueError("Session not found.")
    
    for entry in session.initiative_entries:
        await db.delete(entry)
    
    await db.commit()
    return {"message": "Initiative cleared successfully."}

async def advance_turn(db: AsyncSession, session_id: int) -> Optional[InitiativeEntry]:
    """
    Advances the turn to the next combatant in the initiative order.
    Returns the new active entry, or None if combat ends.
    """
    session = await db.get(CampaignSession, session_id)
    if not session or not session.is_active:
        raise ValueError("No active session found.")

    initiative_order = await get_initiative_order(db, session_id=session_id)
    if not initiative_order:
        session.active_initiative_entry_id = None
        await db.commit()
        return None

    # --- START FIX: More robust logic for advancing the turn ---
    current_active_id = session.active_initiative_entry_id
    if current_active_id is None:
        # If no turn is active, start with the first person in the order.
        next_entry = initiative_order[0]
    else:
        try:
            current_index = [entry.id for entry in initiative_order].index(current_active_id)
            # Move to the next index, or loop back to the start
            next_index = (current_index + 1) % len(initiative_order)
            next_entry = initiative_order[next_index]
        except ValueError:
            # The currently active character is no longer in initiative, start from the top.
            next_entry = initiative_order[0]
    # --- END FIX ---
    
    session.active_initiative_entry_id = next_entry.id
    db.add(session)
    await db.commit()
    
    return next_entry
