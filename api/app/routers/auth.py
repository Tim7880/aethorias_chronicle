# Path: api/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # Standard way to receive username/password
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta # To potentially customize token expiry if needed

from app.db.database import get_db
from app.schemas.token import Token, TokenData
from app.schemas.user import User as UserSchema # Our new Token schema
from app.crud import crud_user
from app.core.security import create_access_token, verify_token_and_get_token_data
from app.core.config import settings
from app.models.user import User as UserModel
from fastapi import WebSocket
from typing import Optional

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/token")

@router.post("/login/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Pass username and password as form data (e.g. x-www-form-urlencoded).
    """
    user = await crud_user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # Standard for 401
        )

    # Access token expires based on settings.ACCESS_TOKEN_EXPIRE_MINUTES
    # You could also create a specific timedelta object here if needed for this endpoint
    # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username} # "sub" (subject) is standard claim for user identifier
        # expires_delta=access_token_expires # Pass if you created a specific timedelta
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- NEW FUNCTION (DEPENDENCY) ---
async def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Dependency to get the current active user from a token.
    To be used in protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token_and_get_token_data(token, credentials_exception)

    user = await crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception # User not found (e.g., deleted after token issued)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

@router.post("/ws-token", response_model=Token)
async def get_websocket_token(current_user: UserModel = Depends(get_current_active_user)):
    """
    Generate a short-lived token specifically for authenticating a WebSocket connection.
    """
    # Create a new token for the current user. You could make this shorter-lived if desired.
    access_token = create_access_token(data={"sub": current_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_token_from_query(websocket: WebSocket) -> Optional[str]:
    query_params = websocket.query_params
    token = query_params.get("token")
    if not token:
        # This case can be handled in the websocket endpoint itself
        return None
    return token