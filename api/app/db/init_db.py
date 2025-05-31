# Path: api/app/db/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.skill import Skill as SkillModel
from app.schemas.skill import SkillCreate as SkillCreateSchema

from app.models.item import Item as ItemModel
from app.models.item import ItemTypeEnum
from app.schemas.item import ItemCreate as ItemCreateSchema

from app.models.spell import Spell as SpellModel
from app.models.spell import SchoolOfMagicEnum
from app.schemas.spell import SpellCreate as SpellCreateSchema

# --- Predefined D&D 5e Skills (ensure this list is complete from previous steps) ---
PREDEFINED_SKILLS = [
    SkillCreateSchema(name="Acrobatics", ability_modifier_name="DEX", description="Your ability to stay on your feet in tricky situations."),
    SkillCreateSchema(name="Animal Handling", ability_modifier_name="WIS", description="Your skill in calming down domesticated animals, keeping a mount from being spooked, or intuiting an animal’s intentions."),
    SkillCreateSchema(name="Arcana", ability_modifier_name="INT", description="Your ability to recall lore about spells, magic items, eldritch symbols, magical traditions, the planes of existence, and the inhabitants of those planes."),
    SkillCreateSchema(name="Athletics", ability_modifier_name="STR", description="Your skill in situations involving swimming, jumping, or climbing."),
    SkillCreateSchema(name="Deception", ability_modifier_name="CHA", description="Your ability to convincingly hide the truth, either verbally or through your actions."),
    SkillCreateSchema(name="History", ability_modifier_name="INT", description="Your ability to recall lore about historical events, legendary people, ancient kingdoms, past disputes, recent wars, and lost civilizations."),
    SkillCreateSchema(name="Insight", ability_modifier_name="WIS", description="Your ability to determine the true intentions of a creature, such as when searching out a lie or predicting someone’s next move."),
    SkillCreateSchema(name="Intimidation", ability_modifier_name="CHA", description="Your ability to influence someone through overt threats, hostile actions, and physical violence."),
    SkillCreateSchema(name="Investigation", ability_modifier_name="INT", description="Your ability to look around for clues and make deductions based on those clues."),
    SkillCreateSchema(name="Medicine", ability_modifier_name="WIS", description="Your ability to stabilize a dying companion or diagnose an illness."),
    SkillCreateSchema(name="Nature", ability_modifier_name="INT", description="Your ability to recall lore about terrain, plants and animals, the weather, and natural cycles."),
    SkillCreateSchema(name="Perception", ability_modifier_name="WIS", description="Your ability to spot, hear, or otherwise detect the presence of something. It measures your general awareness of your surroundings and the keenness of your senses."),
    SkillCreateSchema(name="Performance", ability_modifier_name="CHA", description="Your ability to delight an audience with music, dance, acting, storytelling, or some other form of entertainment."),
    SkillCreateSchema(name="Persuasion", ability_modifier_name="CHA", description="Your ability to influence someone or a group of people with tact, social graces, or good nature."),
    SkillCreateSchema(name="Religion", ability_modifier_name="INT", description="Your ability to recall lore about deities, rites and prayers, religious hierarchies, holy symbols, and the practices of secret cults."),
    SkillCreateSchema(name="Sleight of Hand", ability_modifier_name="DEX", description="Your ability to plant something on someone else, conceal an object on your person, or lift a coin purse."),
    SkillCreateSchema(name="Stealth", ability_modifier_name="DEX", description="Your ability to conceal yourself from enemies, slink past guards, slip away without being noticed, or sneak up on someone without being seen or heard."),
    SkillCreateSchema(name="Survival", ability_modifier_name="WIS", description="Your ability to follow tracks, hunt wild game, guide your group through frozen wastelands, identify signs that owlbears live nearby, predict the weather, or avoid quicksand and other natural hazards.")
]

# --- Predefined D&D 5e Items (ensure this list is comprehensive from previous steps) ---
PREDEFINED_ITEMS = [
    ItemCreateSchema(name="Backpack", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=2.0, properties={"capacity_lbs": 30, "description": "Holds 1 cubic foot or 30 pounds of gear."}),
    ItemCreateSchema(name="Bedroll", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=7.0, cost_gp=1.0),
    ItemCreateSchema(name="Mess Kit", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.2),
    ItemCreateSchema(name="Tinderbox", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.5, properties={"description": "For lighting fires."}),
    ItemCreateSchema(name="Torch", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.01, properties={"duration_hours": 1, "light_radius_ft": "20 bright, 20 dim"}),
    ItemCreateSchema(name="Rations (1 day)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=2.0, cost_gp=0.5),
    ItemCreateSchema(name="Waterskin", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=0.2, properties={"capacity_gallons": 0.5, "full_weight_lbs": 5}),
    ItemCreateSchema(name="Rope, Hempen (50 feet)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=10.0, cost_gp=1.0),
    ItemCreateSchema(name="Thieves' Tools", item_type=ItemTypeEnum.TOOL, weight=1.0, cost_gp=25.0, properties={"use": "Disarm traps, open locks"}),
    ItemCreateSchema(name="Spellbook (Blank)", item_type=ItemTypeEnum.TOOL, weight=3.0, cost_gp=50.0, properties={"description": "A blank spellbook for wizards."}),
    ItemCreateSchema(name="Dagger", item_type=ItemTypeEnum.WEAPON, weight=1.0, cost_gp=2.0, properties={"damage": "1d4 piercing", "type": "simple melee", "properties": ["finesse", "light", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Shortsword", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=10.0, properties={"damage": "1d6 piercing", "type": "martial melee", "properties": ["finesse", "light"]}),
    ItemCreateSchema(name="Longsword", item_type=ItemTypeEnum.WEAPON, weight=3.0, cost_gp=15.0, properties={"damage": "1d8 slashing", "type": "martial melee", "properties": ["versatile (1d10)"]}),
    ItemCreateSchema(name="Light Crossbow", item_type=ItemTypeEnum.WEAPON, weight=5.0, cost_gp=25.0, properties={"damage": "1d8 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "loading", "two-handed"]}),
    ItemCreateSchema(name="Shortbow", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=25.0, properties={"damage": "1d6 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "two-handed"]}),
    ItemCreateSchema(name="Arrows (20)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=1.0),
    ItemCreateSchema(name="Leather Armor", item_type=ItemTypeEnum.ARMOR, weight=10.0, cost_gp=10.0, properties={"ac_base": 11, "armor_type": "light", "dex_bonus": True, "stealth_disadvantage": False}),
    ItemCreateSchema(name="Shield", item_type=ItemTypeEnum.SHIELD, weight=6.0, cost_gp=10.0, properties={"ac_bonus": 2}),
    ItemCreateSchema(name="Potion of Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=50.0, properties={"effect": "Restores 2d4+2 hit points."}),
    ItemCreateSchema(name="Potion of Greater Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=250.0, properties={"effect": "Restores 4d4+4 hit points."}),
]

# --- EXPANDED Predefined D&D 5e Spells ---
PREDEFINED_SPELLS = [
    # Cantrips (Level 0)
    SpellCreateSchema(name="Light", description="You touch one object... sheds bright light...", higher_level=None, range="Touch", components="V, M", material="A firefly or phosphorescent moss", ritual=False, duration="1 hour", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Bard", "Cleric", "Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Mage Hand", description="A spectral, floating hand appears...", higher_level=None, range="30 feet", components="V, S", material=None, ritual=False, duration="1 minute", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.CONJURATION, dnd_classes=["Bard", "Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Ray of Frost", description="A frigid beam of blue-white light streaks towards a creature...", higher_level="The spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8).", range="60 feet", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Prestidigitation", description="This spell is a minor magical trick that novice spellcasters use for practice...", higher_level=None, range="10 feet", components="V, S", material=None, ritual=False, duration="Up to 1 hour", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.TRANSMUTATION, dnd_classes=["Bard", "Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Acid Splash", description="You hurl a bubble of acid...", higher_level="The spell's damage increases by 1d6 when you reach 5th level (2d6), 11th level (3d6), and 17th level (4d6).", range="60 feet", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.CONJURATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Fire Bolt", description="You hurl a mote of fire...", higher_level="The spell's damage increases by 1d10 when you reach 5th level (2d10), 11th level (3d10), and 17th level (4d10).", range="120 feet", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=0, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),


    # Level 1 Spells
    SpellCreateSchema(name="Magic Missile", description="You create three glowing darts...", higher_level="When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st.", range="120 feet", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=1, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Mage Armor", description="You touch a willing creature who isn’t wearing armor...", higher_level=None, range="Touch", components="V, S, M", material="A piece of cured leather", ritual=False, duration="8 hours", concentration=False, casting_time="1 action", level=1, school=SchoolOfMagicEnum.ABJURATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Shield", description="An invisible barrier of magical force appears and protects you...", higher_level=None, range="Self", components="V, S", material=None, ritual=False, duration="1 round", concentration=False, casting_time="1 reaction, which you take when you are hit by an attack or targeted by the magic missile spell", level=1, school=SchoolOfMagicEnum.ABJURATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Sleep", description="This spell sends creatures into a magical slumber...", higher_level="When you cast this spell using a spell slot of 2nd level or higher, you can affect an additional 2d8 hit points of creatures for each slot level above 1st.", range="90 feet", components="V, S, M", material="A pinch of fine sand, rose petals, or a cricket", ritual=False, duration="1 minute", concentration=False, casting_time="1 action", level=1, school=SchoolOfMagicEnum.ENCHANTMENT, dnd_classes=["Bard", "Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Burning Hands", description="As you hold your hands with thumbs touching and fingers spread, a thin sheet of flames shoots forth...", higher_level="When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d6 for each slot level above 1st.", range="Self (15-foot cone)", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=1, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Charm Person", description="You attempt to charm a humanoid you can see within range...", higher_level="When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.", range="30 feet", components="V, S", material=None, ritual=False, duration="1 hour", concentration=False, casting_time="1 action", level=1, school=SchoolOfMagicEnum.ENCHANTMENT, dnd_classes=["Bard", "Druid", "Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Feather Fall", description="Choose up to five falling creatures within range...", higher_level=None, range="60 feet", components="V, M", material="A small feather or a piece of down", ritual=False, duration="1 minute", concentration=False, casting_time="1 reaction, which you take when you or a creature within 60 feet of you falls", level=1, school=SchoolOfMagicEnum.TRANSMUTATION, dnd_classes=["Bard", "Sorcerer", "Wizard"], source_book="SRD"),

    # Level 2 Spells
    SpellCreateSchema(name="Misty Step", description="Briefly surrounded by silvery mist, you teleport up to 30 feet to an unoccupied space that you can see.", higher_level=None, range="Self", components="V", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 bonus action", level=2, school=SchoolOfMagicEnum.CONJURATION, dnd_classes=["Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Mirror Image", description="Three illusory duplicates of yourself appear in your space...", higher_level=None, range="Self", components="V, S", material=None, ritual=False, duration="1 minute", concentration=False, casting_time="1 action", level=2, school=SchoolOfMagicEnum.ILLUSION, dnd_classes=["Bard", "Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Scorching Ray", description="You create three rays of fire and hurl them at targets within range...", higher_level="When you cast this spell using a spell slot of 3rd level or higher, you create one additional ray for each slot level above 2nd.", range="120 feet", components="V, S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=2, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Web", description="You conjure a mass of thick, sticky webbing at a point of your choice within range...", higher_level=None, range="60 feet", components="V, S, M", material="A bit of spiderweb", ritual=False, duration="Concentration, up to 1 hour", concentration=True, casting_time="1 action", level=2, school=SchoolOfMagicEnum.CONJURATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),

    # Level 3 Spells
    SpellCreateSchema(name="Fireball", description="A bright streak flashes from your pointing finger...", higher_level="When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.", range="150 feet", components="V, S, M", material="A tiny ball of bat guano and sulfur", ritual=False, duration="Instantaneous", concentration=False, casting_time="1 action", level=3, school=SchoolOfMagicEnum.EVOCATION, dnd_classes=["Sorcerer", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Fly", description="You touch a willing creature. The target gains a flying speed of 60 feet for the duration.", higher_level="When you cast this spell using a spell slot of 4th level or higher, you can target one additional creature for each slot level above 3rd.", range="Touch", components="V, S, M", material="A wing feather from any bird", ritual=False, duration="Concentration, up to 10 minutes", concentration=True, casting_time="1 action", level=3, school=SchoolOfMagicEnum.TRANSMUTATION, dnd_classes=["Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    SpellCreateSchema(name="Counterspell", description="You attempt to interrupt a creature in the process of casting a spell...", higher_level="If you cast this spell using a spell slot of 4th level or higher, the interrupted spell has no effect if its level is less than or equal to the level of the spell slot you used.", range="60 feet", components="S", material=None, ritual=False, duration="Instantaneous", concentration=False, casting_time="1 reaction, which you take when you see a creature within 60 feet of you casting a spell", level=3, school=SchoolOfMagicEnum.ABJURATION, dnd_classes=["Sorcerer", "Warlock", "Wizard"], source_book="SRD"),
    
    # Ensure your enums and schema fields can handle all data.
    # Add more spells from SRD as needed.
]


async def seed_skills(db: AsyncSession) -> None:
    # ... (seed_skills function remains the same) ...
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
    # ... (seed_items function remains the same) ...
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

async def seed_spells(db: AsyncSession) -> None: # This function should already exist from your previous work
    print("Attempting to seed spells...")
    spells_added_in_this_run = 0
    for spell_data in PREDEFINED_SPELLS:
        result = await db.execute(select(SpellModel).filter(SpellModel.name == spell_data.name))
        existing_spell = result.scalars().first()

        if not existing_spell:
            # Ensure all fields in SpellCreateSchema match SpellModel constructor if using **
            # Or map them explicitly:
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
                school=spell_data.school, # This expects the Enum member
                dnd_classes=spell_data.dnd_classes, # This is JSON
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
