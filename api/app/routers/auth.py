from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Standard way to receive username/password
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta # To potentially customize token expiry if needed

from app.db.database import get_db
from app.schemas.token import Token # Our new Token schema
from app.crud import crud_user
from app.core.security import create_access_token
from app.core.config import settings # For ACCESS_TOKEN_EXPIRE_MINUTES if not passed directly

router = APIRouter(tags=["Authentication"])

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