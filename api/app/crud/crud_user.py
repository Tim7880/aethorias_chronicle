from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # For SQLAlchemy 1.4+ style, or just `from sqlalchemy import select` for 2.0+
# If using SQLAlchemy 2.0, `select` is directly from `sqlalchemy`
# from sqlalchemy import select # Use this for SQLAlchemy 2.0

from app.models.user import User as UserModel
from app.schemas.user import UserCreate as UserCreateSchema
from app.core.security import get_password_hash # Import our password hashing function
# ... (other imports remain the same)
# from app.core.security import get_password_hash # Already there
from app.core.security import verify_password # <--- ADD THIS IMPORT

# ... (get_user_by_id, get_user_by_email, get_user_by_username, create_user functions remain the same) ...

# --- NEW FUNCTION ---
async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserModel | None:
    """
    Authenticates a user by username and password.

    Args:
        db: The database session.
        username: The username to authenticate.
        password: The plain text password to verify.

    Returns:
        The User model instance if authentication is successful, otherwise None.
    """
    user = await get_user_by_username(db, username=username)
    if not user:
        return None # User not found
    if not verify_password(password, user.hashed_password):
        return None # Password incorrect
    return user # Authentication successful

async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel | None:
    """
    Retrieves a user by their ID.
    """
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> UserModel | None:
    """
    Retrieves a user by their email address.
    Useful for checking if an email is already registered.
    """
    result = await db.execute(select(UserModel).filter(UserModel.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> UserModel | None:
    """
    Retrieves a user by their username.
    Useful for login or checking if a username is taken.
    """
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreateSchema) -> UserModel:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        preferred_timezone=user.preferred_timezone 
        # is_active and is_superuser will use server defaults from the model
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) # Refresh to get DB-generated values like ID, created_at
    return db_user

# We can add update and delete functions here later as needed.
# For example:
# async def update_user(db: AsyncSession, user: UserModel, user_update: UserUpdateSchema) -> UserModel:
#     ...
# async def delete_user(db: AsyncSession, user_id: int) -> UserModel | None:
#     ...