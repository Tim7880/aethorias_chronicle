from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db # Our dependency to get a DB session
from app.schemas.user import UserCreate, User as UserSchema # Pydantic schemas
from app.crud import crud_user # Our CRUD functions for users

router = APIRouter(
    prefix="/api/v1/users", # All routes in this router will start with /users
    tags=["Users"]          # For grouping in API docs
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    - **username**: Each username must be unique.
    - **email**: Each email must be unique.
    - **password**: Must be at least 8 characters.
    """
    # Check if user with this username already exists
    existing_user_by_username = await crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )
    
    # Check if user with this email already exists
    existing_user_by_email = await crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    
    # If username and email are unique, create the new user
    created_user = await crud_user.create_user(db=db, user=user_in)
    return created_user

# We can add more user-related endpoints here later, e.g.:
# - Get current user details (requires authentication)
# - Update user details
# - etc.