# Path: api/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 

from app.db.database import get_db
from app.schemas.user import UserCreate, User as UserSchema, UserPasswordChange
from app.schemas.campaign import CampaignMember as CampaignMemberSchema
from app.crud import crud_user
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/users", 
    tags=["Users"]       
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    existing_user_by_username = await crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )
    existing_user_by_email = await crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    created_user = await crud_user.create_user(db=db, user=user_in)
    return created_user

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user

@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_current_user_password(
    password_data: UserPasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    await crud_user.update_user_password(
        db=db, user_to_update=current_user, new_password=password_data.new_password
    )
    return # No content

# --- NEW ENDPOINT for fetching current user's campaign memberships/requests ---
@router.get("/me/campaign-memberships/", response_model=List[CampaignMemberSchema])
async def read_my_campaign_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Retrieve all campaign memberships (pending, active, rejected, etc.) for the current user.
    """
    memberships = await crud_user.get_user_campaign_memberships(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return memberships
# --- END NEW ENDPOINT ---



