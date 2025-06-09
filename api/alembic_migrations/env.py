# Path: api/alembic_migrations/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Aethoria's Chronicle Specific Model Imports ---
# Add your model's MetaData object here for 'autogenerate' support
# Ensure all models are imported here so Base.metadata knows about them.
from app.db.base_class import Base as AppBase  # Import your app's Base
from app.core.config import settings as app_settings # Use app's settings

# Import all your application's models
from app.models.user import User
from app.models.character import Character
from app.models.campaign import Campaign
from app.models.campaign_member import CampaignMember
from app.models.skill import Skill
from app.models.character_skill import CharacterSkill
from app.models.item import Item  # <--- ADDED IMPORT
from app.models.character_item import CharacterItem 
from app.models.spell import Spell
from app.models.character_spell import CharacterSpell
from app.models.monster import Monster
target_metadata = AppBase.metadata
# --- End Aethoria's Chronicle Specific ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url") # Gets sync URL from alembic.ini
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        app_settings.DATABASE_URL, # Use the async URL from your app's settings
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())




    