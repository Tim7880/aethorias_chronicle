# Path: api/app/crud/crud_user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update # Add update if you were to build a generic update
from typing import Optional

from app.models.user import User as UserModel
from app.schemas.user import UserCreate as UserCreateSchema
# from app.schemas.user import UserUpdate as UserUpdateSchema # Not used yet
from app.core.security import get_password_hash, verify_password # verify_password was for authenticate_user

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

# --- NEW FUNCTION ---
async def update_user_password(
    db: AsyncSession, *, user_to_update: UserModel, new_password: str
) -> UserModel:
    """
    Updates a user's password.
    `user_to_update` is the existing SQLAlchemy model instance from the DB.
    """
    new_hashed_password = get_password_hash(new_password)
    user_to_update.hashed_password = new_hashed_password
    db.add(user_to_update) # Add the updated object to the session to mark it as dirty
    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update