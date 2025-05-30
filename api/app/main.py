# Path: api/app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, AsyncSessionLocal 
from app.db import base 
from app.db.init_db import seed_skills, seed_items, seed_spells
    
from app.routers import users as user_router 
from app.routers import auth as auth_router
from app.routers import characters as character_router
from app.routers import campaigns as campaign_router
from app.routers import skills as skill_router
from app.routers import items as item_router
from app.routers import spells as spell_router
from app.routers import admin as admin_router # <--- IMPORT THE NEW ADMIN ROUTER


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Ensuring database tables exist via Alembic (manual step) or create_all (dev)...")
    async with engine.begin() as conn:
        # For production, Alembic handles schema. For dev, create_all ensures tables exist if DB is new.
        # await conn.run_sync(base.Base.metadata.drop_all) 
        await conn.run_sync(base.Base.metadata.create_all) 
    
    print("Application startup: Seeding initial data...")
    async with AsyncSessionLocal() as db_session:
        await seed_skills(db_session)
        await db_session.commit()

        await seed_items(db_session)
        await db_session.commit()

        await seed_spells(db_session)
        await db_session.commit()
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
app.include_router(skill_router.router, prefix=settings.API_V1_STR)
app.include_router(item_router.router, prefix=settings.API_V1_STR)
app.include_router(spell_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR) # <--- INCLUDE THE ADMIN ROUTER

@app.get("/")
async def read_root():
    return {"message": f"Welcome to the Scriptorium of {settings.PROJECT_NAME}!"}

@app.get("/health")
async def health_check():
    return {"status": "API is healthy and running"}



