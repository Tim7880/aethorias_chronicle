# Path: api/app/crud/crud_user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload 
from typing import Optional, List

from app.models.user import User as UserModel
from app.models.campaign_member import CampaignMember as CampaignMemberModel
from app.models.campaign import Campaign as CampaignModel 
from app.models.character import Character as CharacterModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel 
from app.models.item import Item as ItemModel 
from app.models.character_item import CharacterItem as CharacterItemModel 
from app.models.spell import Spell as SpellModel 
from app.models.character_spell import CharacterSpell as CharacterSpellModel 

from app.schemas.user import UserCreate as UserCreateSchema
from app.core.security import get_password_hash, verify_password

async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel | None:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> UserModel | None:
    result = await db.execute(select(UserModel).filter(UserModel.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> UserModel | None:
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreateSchema) -> UserModel:
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        preferred_timezone=user.preferred_timezone 
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserModel | None:
    user = await get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def update_user_password(
    db: AsyncSession, *, user_to_update: UserModel, new_password: str
) -> UserModel:
    new_hashed_password = get_password_hash(new_password)
    user_to_update.hashed_password = new_hashed_password
    db.add(user_to_update)
    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update

async def get_user_campaign_memberships(
    db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[CampaignMemberModel]:
    """
    Retrieves all campaign memberships for a given user.
    Eagerly loads associated campaign (and its DM), user, and character 
    (including character's skills, inventory items, and known spells).
    """
    print(f"--- ENTERING get_user_campaign_memberships for user_id: {user_id} ---") # Entry print
    result = await db.execute(
       select(CampaignMemberModel)
       .options(
           selectinload(CampaignMemberModel.campaign).options(
           selectinload(CampaignModel.dm) 
          ),
           selectinload(CampaignMemberModel.user), 
           selectinload(CampaignMemberModel.character).options(
               selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
               selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
               selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
          )
        )
        .filter(CampaignMemberModel.user_id == user_id)
        .order_by(CampaignMemberModel.joined_at.desc())
        .offset(skip)
        .limit(limit)
    )
    memberships = result.scalars().all()

    # --- DEBUGGING PRINT STATEMENT ---
    print(f"--- Debugging get_user_campaign_memberships (after query) for user_id: {user_id} ---")
    if not memberships:
        print("No memberships found in DB query.")
    for i, membership_item in enumerate(memberships): # Changed 'membership' to 'membership_item' to avoid conflict
        print(f"Membership Item {i+1} (ID: {membership_item.id}, Status: {membership_item.status}, Campaign FK ID: {membership_item.campaign_id}):")
        if membership_item.campaign:
            print(f"  Campaign ID: {membership_item.campaign.id}, Title: '{membership_item.campaign.title}', DM ID: {membership_item.campaign.dm_user_id}")
            if membership_item.campaign.dm:
                print(f"    Campaign DM Username: {membership_item.campaign.dm.username}")
            else:
                print("    Campaign DM object not loaded or is None.")
        else:
            print(f"  Campaign data (membership_item.campaign) is None or not loaded for membership ID {membership_item.id}.")
        
        if membership_item.user:
             print(f"  User ID: {membership_item.user.id}, Username: '{membership_item.user.username}'")
        else:
            print(f"  User data not loaded for membership ID {membership_item.id}.")

        if membership_item.character:
            print(f"  Character ID: {membership_item.character.id}, Name: '{membership_item.character.name}'")
        else:
            print(f"  No character associated with this membership.")
    print("--- End Debugging ---")
    # --- END DEBUGGING PRINT STATEMENT ---

    return memberships


