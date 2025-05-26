from fastapi import FastAPI
from app.db.database import engine
from app.db import base 
from app.routers import users as user_router
from app.routers import auth as auth_router # <--- IMPORT THE NEW AUTH ROUTER
from app.core.config import settings

async def create_db_and_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(base.Base.metadata.drop_all) 
        await conn.run_sync(base.Base.metadata.create_all)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    on_startup=[create_db_and_tables]
)

# Include routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)  # <--- INCLUDE THE AUTH ROUTER
app.include_router(user_router.router, prefix=settings.API_V1_STR) # User router is still included

@app.get("/")
async def read_root():
    return {"message": f"Welcome to the Scriptorium of {settings.PROJECT_NAME}!"}

@app.get("/health")
async def health_check():
    return {"status": "API is healthy and running"}