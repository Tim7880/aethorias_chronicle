# Path: api/app/db/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import CRUD modules
from app.crud import crud_skill, crud_item, crud_spell, crud_monster, crud_dnd_class, crud_race, crud_background


# Import models
from app.models.skill import Skill as SkillModel
from app.models.item import Item as ItemModel
from app.models.spell import Spell as SpellModel
from app.models.monster import Monster as MonsterModel
from app.models.dnd_class import DndClass as DndClassModel
from app.models.race import Race as RaceModel
from app.models.background import Background as BackgroundModel

# Import schemas
from app.schemas.skill import SkillCreate
from app.schemas.item import ItemCreate
from app.schemas.spell import SpellCreate
from app.schemas.monster import MonsterCreate
from app.schemas.dnd_class import DndClassCreate
from app.schemas.race import RaceCreate
from app.schemas.background import BackgroundCreate

# --- Import data from separate files ---
from app.game_data.skills_data import PREDEFINED_SKILLS
from app.game_data.items_data import PREDEFINED_ITEMS
from app.game_data.spells_data import PREDEFINED_SPELLS
from app.game_data.monsters_data import PREDEFINED_MONSTERS
from app.game_data.classes_data import PREDEFINED_CLASSES_DATA
from app.game_data.races_data import PREDEFINED_RACES 
from app.game_data.backgrounds_data import PREDEFINED_BACKGROUNDS

async def seed_skills(db: AsyncSession) -> None:
    print("Attempting to seed skills...")
    for skill_data in PREDEFINED_SKILLS:
        existing = await db.execute(select(SkillModel).filter_by(name=skill_data.name))
        if not existing.scalars().first():
            db.add(SkillModel(**skill_data.model_dump()))
            print(f"Adding skill: {skill_data.name}")
    await db.commit()
    print("Skill seeding process complete.")

async def seed_items(db: AsyncSession) -> None:
    print("Attempting to seed items...")
    for item_data in PREDEFINED_ITEMS:
        existing = await db.execute(select(ItemModel).filter_by(name=item_data.name))
        if not existing.scalars().first():
            db.add(ItemModel(**item_data.model_dump()))
            print(f"Adding item: {item_data.name}")
    await db.commit()
    print("Item seeding process complete.")

async def seed_spells(db: AsyncSession) -> None:
    print("Attempting to seed spells...")
    for spell_data in PREDEFINED_SPELLS:
        existing = await db.execute(select(SpellModel).filter_by(name=spell_data.name))
        if not existing.scalars().first():
            db.add(SpellModel(**spell_data.model_dump()))
            print(f"Adding spell: {spell_data.name}")
    await db.commit()
    print("Spell seeding process complete.")

async def seed_monsters(db: AsyncSession) -> None:
    print("Attempting to seed monsters...")
    for monster_data in PREDEFINED_MONSTERS:
        existing = await crud_monster.get_monster_by_name(db=db, name=monster_data["name"])
        if not existing:
            await crud_monster.create_monster(db=db, monster_in=MonsterCreate(**monster_data))
            print(f"Adding monster: {monster_data['name']}")
    print("Monster seeding process complete.")

async def seed_dnd_classes(db: AsyncSession) -> None:
    print("Attempting to seed D&D classes...")
    for class_info in PREDEFINED_CLASSES_DATA:
        class_name = class_info["class_data"]["name"]
        existing_class = await crud_dnd_class.get_dnd_class_by_name(db=db, name=class_name)
        if not existing_class:
            class_create_schema = DndClassCreate(**class_info["class_data"], levels=class_info["levels"])
            await crud_dnd_class.create_dnd_class(db=db, dnd_class_in=class_create_schema)
            print(f"Adding class: {class_name}")
    print("D&D class seeding process complete.")


async def seed_races(db: AsyncSession) -> None:
    print("Attempting to seed races...")
    for race_data in PREDEFINED_RACES:
        existing_race = await crud_race.get_race_by_name(db=db, name=race_data["name"])
        if not existing_race:
            race_in = RaceCreate(**race_data)
            await crud_race.create_race(db=db, race_in=race_in)
            print(f"Adding race: {race_data['name']}")
    print("Race seeding process complete.")

async def seed_backgrounds(db: AsyncSession) -> None:
    print("Attempting to seed backgrounds...")
    for background_data in PREDEFINED_BACKGROUNDS:
        existing_background = await crud_background.get_background_by_name(db=db, name=background_data["name"])
        if not existing_background:
            background_in = BackgroundCreate(**background_data)
            await crud_background.create_background(db=db, background_in=background_in)
            print(f"Adding background: {background_data['name']}")
    print("Background seeding process complete.")

async def init_db(db: AsyncSession) -> None:
    print("Application startup: Seeding initial data...")
    await seed_skills(db)
    await seed_items(db)
    await seed_spells(db)
    await seed_monsters(db)
    await seed_dnd_classes(db)
    await seed_races(db)
    await seed_backgrounds(db) 
    print("Initial data seeding complete.")

