# Path: api/app/db/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import CRUD modules
from app.crud import crud_skill, crud_item, crud_spell, crud_monster, crud_dnd_class

# Import models
from app.models.skill import Skill as SkillModel
from app.models.item import Item as ItemModel, ItemTypeEnum
from app.models.spell import Spell as SpellModel, SchoolOfMagicEnum
from app.models.monster import Monster as MonsterModel # <--- NEW IMPORT
from app.models.dnd_class import DndClass as DndClassModel, ClassLevel as ClassLevelModel 
# Import schemas
from app.schemas.skill import SkillCreate as SkillCreateSchema
from app.schemas.item import ItemCreate as ItemCreateSchema
from app.schemas.spell import SpellCreate as SpellCreateSchema
from app.schemas.monster import MonsterCreate as MonsterCreateSchema # <--- NEW IMPORT
from app.schemas.dnd_class import DndClassCreate, ClassLevelCreate

# --- MODIFICATION: Import data from separate files ---
from app.game_data.skills_data import PREDEFINED_SKILLS
from app.game_data.items_data import PREDEFINED_ITEMS
from app.game_data.spells_data import PREDEFINED_SPELLS
from app.game_data.monsters_data import PREDEFINED_MONSTERS
from app.game_data.classes_data import PREDEFINED_CLASSES_DATA
# --- END MODIFICATION ---

async def seed_skills(db: AsyncSession) -> None:
    print("Attempting to seed skills...")
    skills_added_in_this_run = 0
    for skill_data in PREDEFINED_SKILLS:
        result = await db.execute(select(SkillModel).filter(SkillModel.name == skill_data.name))
        existing_skill = result.scalars().first()
        if not existing_skill:
            db_skill = SkillModel(**skill_data.model_dump())
            db.add(db_skill)
            print(f"Adding skill: {skill_data.name}")
            skills_added_in_this_run += 1
    if skills_added_in_this_run > 0:
        try:
            await db.commit()
            print(f"Successfully added {skills_added_in_this_run} new skills and committed.")
        except Exception as e:
            await db.rollback(); print(f"Error during skill seeding commit: {e}")
    else:
        print("No new skills to add. Database skill list appears up to date.")

async def seed_items(db: AsyncSession) -> None:
    print("Attempting to seed items...")
    items_added_in_this_run = 0
    for item_data in PREDEFINED_ITEMS:
        result = await db.execute(select(ItemModel).filter(ItemModel.name == item_data.name))
        existing_item = result.scalars().first()
        if not existing_item:
            db_item = ItemModel(**item_data.model_dump())
            db.add(db_item)
            print(f"Adding item: {item_data.name}")
            items_added_in_this_run += 1
    if items_added_in_this_run > 0:
        try:
            await db.commit(); print(f"Successfully added {items_added_in_this_run} new items and committed.")
        except Exception as e:
            await db.rollback(); print(f"Error during item seeding commit: {e}")
    else:
        print("No new items to add. Database item list appears up to date.")

async def seed_spells(db: AsyncSession) -> None:
    print("Attempting to seed spells...")
    spells_added_in_this_run = 0
    for spell_data in PREDEFINED_SPELLS:
        result = await db.execute(select(SpellModel).filter(SpellModel.name == spell_data.name))
        existing_spell = result.scalars().first()

        if not existing_spell:
            db_spell = SpellModel(
                name=spell_data.name,
                description=spell_data.description,
                higher_level=spell_data.higher_level,
                range=spell_data.range,
                components=spell_data.components,
                material=spell_data.material,
                ritual=spell_data.ritual,
                duration=spell_data.duration,
                concentration=spell_data.concentration,
                casting_time=spell_data.casting_time,
                level=spell_data.level,
                school=spell_data.school,
                dnd_classes=spell_data.dnd_classes,
                source_book=spell_data.source_book
            )
            db.add(db_spell)
            print(f"Adding spell: {spell_data.name}")
            spells_added_in_this_run += 1
            
    if spells_added_in_this_run > 0:
        try:
            await db.commit()
            print(f"Successfully added {spells_added_in_this_run} new spells and committed.")
        except Exception as e:
            await db.rollback()
            print(f"Error during spell seeding commit: {e}")
    else:
        print("No new spells to add. Database spell list appears up to date.")

# --- NEW FUNCTION to seed monsters ---
async def seed_monsters(db: AsyncSession) -> None:
    print("Attempting to seed monsters...")
    monsters_added_in_this_run = 0
    for monster_data in PREDEFINED_MONSTERS:
        existing_monster = await crud_monster.get_monster_by_name(db=db, name=monster_data["name"])
        if not existing_monster:
            monster_in = MonsterCreateSchema(**monster_data)
            await crud_monster.create_monster(db=db, monster_in=monster_in)
            print(f"Adding monster: {monster_data['name']}")
            monsters_added_in_this_run += 1
    
    # A single commit after adding all new monsters is more efficient
    if monsters_added_in_this_run > 0:
        print(f"Successfully added {monsters_added_in_this_run} new monsters.")
    else:
        print("No new monsters to add. Database monster list appears up to date.")
# --- END NEW ---

# --- START MODIFICATION: Updated seeding function ---
async def seed_dnd_classes(db: AsyncSession) -> None:
    print("Attempting to seed D&D classes...")
    classes_added_count = 0
    for class_info in PREDEFINED_CLASSES_DATA:
        class_name = class_info["class_data"]["name"]
        existing_class = await crud_dnd_class.get_dnd_class_by_name(db=db, name=class_name)
        if not existing_class:
            # Construct the Pydantic schema object from the dictionary data
            class_create_schema = DndClassCreate(**class_info["class_data"], levels=class_info["levels"])
            
            # Call the CRUD function with the fully formed schema object
            await crud_dnd_class.create_dnd_class(db=db, dnd_class_in=class_create_schema)
            
            print(f"Adding class: {class_name}")
            classes_added_count += 1
            
    if classes_added_count > 0:
        print(f"Successfully added {classes_added_count} new D&D classes.")
    else:
        print("No new D&D classes to add. Database class list appears up to date.")
# --- END MODIFICATION ---

# --- NEW: Main function to call all seeders ---
async def init_db(db: AsyncSession) -> None:
    # This function will be called by your application on startup.
    # It ensures all necessary data is seeded.
    print("Application startup: Seeding initial data...")
    await seed_skills(db)
    await seed_items(db)
    await seed_spells(db)
    await seed_monsters(db)
    await seed_dnd_classes(db)
    print("Initial data seeding complete.")
