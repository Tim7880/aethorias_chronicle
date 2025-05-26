from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Aethoria's Chronicle API"
    API_V1_STR: str = "/api/v1"

    # Database settings
    # Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE_NAME
    # Example for Docker setup:
    DATABASE_URL: str = "postgresql+asyncpg://aethoria_user:aethoria_password@localhost:5432/aethoria_db"
    # For production, you'd get this from an environment variable

    # JWT settings (for authentication later)
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env_variable" # CHANGE THIS!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token expiry time

    class Config:
        env_file = ".env" # If you want to use a .env file for overrides
        env_file_encoding = 'utf-8'

@lru_cache() # Cache the settings object so it's only created once
def get_settings():
    return Settings()

settings = get_settings()