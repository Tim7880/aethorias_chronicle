from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel): # For decoding token later, not used by login endpoint directly
    username: str | None = None
