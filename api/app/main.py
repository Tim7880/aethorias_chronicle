# Path: api/app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, AsyncSessionLocal
from app.db import base 
from app.db.init_db import seed_skills
    
from app.routers import users as user_router 
from app.routers import auth as auth_router
from app.routers import characters as character_router
from app.routers import campaigns as campaign_router
from app.routers import skills as skill_router # <--- IMPORT THE NEW SKILL ROUTER


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Creating database tables if they don't exist...")
    async with engine.begin() as conn:
        # await conn.run_sync(base.Base.metadata.drop_all)
        await conn.run_sync(base.Base.metadata.create_all) 
    
    print("Application startup: Seeding initial data (skills)...")
    async with AsyncSessionLocal() as db_session:
        await seed_skills(db_session)
    print("Application startup complete.")
    
    yield
    
    print("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    lifespan=lifespan
)

# Include routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(user_router.router, prefix=settings.API_V1_STR) 
app.include_router(character_router.router, prefix=settings.API_V1_STR)
app.include_router(campaign_router.router, prefix=settings.API_V1_STR)
app.include_router(skill_router.router, prefix=settings.API_V1_STR) # <--- INCLUDE THE SKILL ROUTER

@app.get("/")
async def read_root():
    return {"message": f"Welcome to the Scriptorium of {settings.PROJECT_NAME}!"}

@app.get("/health")
async def health_check():
    return {"status": "API is healthy and running"}


