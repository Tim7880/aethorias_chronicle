from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings # Import settings from our config file
from typing import AsyncGenerator

# Create the SQLAlchemy async engine
# For async, we use 'postgresql+asyncpg://...'
engine = create_async_engine(
    settings.DATABASE_URL,
    # echo=True # Set to True to see SQL queries in console (good for debugging)
)

# Create a sessionmaker to generate AsyncSession instances
# expire_on_commit=False is often recommended for FastAPI background tasks
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for our SQLAlchemy models to inherit from
Base = declarative_base()

# Dependency to get a DB session in path operations
async def get_db() -> AsyncGenerator[AsyncSession, None]: # <--- MODIFIED RETURN TYPE HINT
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # We typically don't commit or rollback in the dependency itself.
            # The commit/rollback should happen in the CRUD function or endpoint
            # after the work with the session is done.
            # If an exception occurs before yield, it will propagate and FastAPI handles it.
            # If after yield, the finally block ensures closure.
        except Exception as e:
            # If you want to specifically handle rollback here, you can,
            # but often it's handled at a higher level or by FastAPI's error handling.
            # await session.rollback() # Optional: if you want explicit rollback on error during session use
            raise e # Re-raise the exception
        finally:
            await session.close()