# Path: api/app/schemas/token.py
from pydantic import BaseModel
from typing import Optional # Ensure Optional is imported if using Python < 3.10 for `| None`

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

    