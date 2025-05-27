# Path: api/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    preferred_timezone: Optional[str] = 'UTC'

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Properties to receive via API on update (general user update)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    # Note: We typically don't update password via this generic update schema directly
    # password: Optional[str] = Field(None, min_length=8) 
    preferred_timezone: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# --- NEW SCHEMA FOR PASSWORD CHANGE ---
class UserPasswordChange(BaseModel):
    new_password: str = Field(..., min_length=8)
    # current_password: Optional[str] = None # Optional: if we want to verify current pass

# Properties stored in DB, includes hashed_password
class UserInDBBase(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic V2, replaces orm_mode

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Properties to return to client (never return hashed_password)
class User(UserInDBBase):
    pass

