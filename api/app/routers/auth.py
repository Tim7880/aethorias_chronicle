# Path: api/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Query, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.schemas.token import Token, TokenData
from app.crud import crud_user
from app.core.security import create_access_token, verify_token_and_get_token_data
from app.models.user import User as UserModel

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/token")

@router.post("/login/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud_user.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_active_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserModel:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_token_and_get_token_data(token, credentials_exception)
    user = await crud_user.get_user_by_username(db, username=token_data.username)
    if user is None or not user.is_active:
        raise credentials_exception
    return user

@router.post("/ws-token", response_model=Token)
async def get_websocket_token(current_user: UserModel = Depends(get_current_active_user)):
    access_token = create_access_token(data={"sub": current_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_user_from_websocket_token(token: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)) -> UserModel:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    if token is None:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
    try:
        token_data = verify_token_and_get_token_data(token, credentials_exception)
        if token_data.username is None: raise credentials_exception
        user = await crud_user.get_user_by_username(db, username=token_data.username)
        if user is None or not user.is_active: raise credentials_exception
        return user
    except HTTPException:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication credentials")
