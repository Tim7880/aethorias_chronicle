# Path: api/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List # For List[CharacterSchema] later if added here

from app.db.database import get_db
from app.schemas.user import UserCreate, User as UserSchema, UserPasswordChange # <--- ADD UserPasswordChange
from app.crud import crud_user
from app.models.user import User as UserModel
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/v1/users", 
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

# --- NEW ENDPOINT ---
@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_current_user_password(
    password_data: UserPasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Change current user's password.
    """
    # Optional: If UserPasswordChange included current_password, verify it here:
    # if not verify_password(password_data.current_password, current_user.hashed_password):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

    await crud_user.update_user_password(
        db=db, user_to_update=current_user, new_password=password_data.new_password
    )
    # No content returned on successful password change, just a 204 status.
    return

