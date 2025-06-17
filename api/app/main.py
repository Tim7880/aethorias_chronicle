# Path: api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, AsyncSessionLocal 
from app.db import base 
from app.db.init_db import seed_skills, seed_items, seed_spells, seed_monsters, seed_dnd_classes, seed_races, seed_backgrounds, seed_conditions


# Import all routers
from app.routers import users as user_router 
from app.routers import auth as auth_router
from app.routers import characters as character_router
from app.routers import campaigns as campaign_router
from app.routers import campaign_members as campaign_member_router
from app.routers import skills as skill_router
from app.routers import items as item_router
from app.routers import spells as spell_router
from app.routers import monsters as monster_router
from app.routers import dnd_classes as dnd_class_router
from app.routers import races as race_router
from app.routers import backgrounds as background_router
from app.routers import conditions as condition_router
from app.routers import admin as admin_router
from app.routers import websockets
from app.routers import campaign_sessions

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Ensuring database tables exist via Alembic (manual step) or create_all (dev)...")
    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all) 
    
    print("Application startup: Seeding initial data...")
    async with AsyncSessionLocal() as db_session:
        await seed_skills(db_session)
        await seed_items(db_session)
        await seed_spells(db_session)
        await seed_monsters(db_session)
        await seed_dnd_classes(db_session)
        await seed_races(db_session)
        await seed_backgrounds(db_session)
        await seed_conditions(db_session) # <--- ADDED call to seed races

    print("Application startup complete.")
    
    yield
    
    print("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    lifespan=lifespan
)

# CORS Middleware setup
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(user_router.router, prefix=settings.API_V1_STR) 
app.include_router(character_router.router, prefix=settings.API_V1_STR)
app.include_router(campaign_router.router, prefix=settings.API_V1_STR)
app.include_router(campaign_member_router.router, prefix=settings.API_V1_STR)
app.include_router(skill_router.router, prefix=settings.API_V1_STR)
app.include_router(item_router.router, prefix=settings.API_V1_STR)
app.include_router(spell_router.router, prefix=settings.API_V1_STR)
app.include_router(monster_router.router, prefix=settings.API_V1_STR)
app.include_router(dnd_class_router.router, prefix=settings.API_V1_STR)
app.include_router(race_router.router, prefix=settings.API_V1_STR)
app.include_router(background_router.router, prefix=settings.API_V1_STR)
app.include_router(condition_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router)
app.include_router(campaign_sessions.router)

@app.get("/")
async def read_root():
    return {"message": f"Welcome to the Scriptorium of {settings.PROJECT_NAME}!"}

@app.get("/health")
async def health_check():
    return {"status": "API is healthy and running"}

