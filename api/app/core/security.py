from passlib.context import CryptContext
from jose import JWTError, jwt # For JWT creation and error handling
from datetime import datetime, timedelta, timezone # timezone for Python 3.9+
from typing import Optional

from app.core.config import settings # Our settings (SECRET_KEY, ALGORITHM, EXPIRE_MINUTES)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- NEW/UPDATED FUNCTION ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data: The data to encode in the token (typically user identifier like username or id).
        expires_delta: Optional timedelta object for custom expiry. 
                       If None, uses default from settings.

    Returns:
        The encoded JWT access token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Use timezone.utc for datetime.now() to ensure it's timezone-aware
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "sub": str(data.get("sub"))}) # 'sub' (subject) is standard for user ID/name
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# We will add a function to decode/validate tokens later when we protect endpoints
# def verify_token(token: str, credentials_exception):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         # You might want to create a Pydantic schema for the token data
#         # token_data = TokenData(username=username) 
#     except JWTError:
#         raise credentials_exception
#     return username # or token_data