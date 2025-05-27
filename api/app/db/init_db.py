# Path: api/app/db/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.skill import Skill as SkillModel
from app.schemas.skill import SkillCreate as SkillCreateSchema

from app.models.item import Item as ItemModel # <--- NEW IMPORT
from app.models.item import ItemTypeEnum # <--- NEW IMPORT
from app.schemas.item import ItemCreate as ItemCreateSchema

from app.models.spell import Spell as SpellModel # <--- NEW IMPORT
from app.models.spell import SchoolOfMagicEnum # <--- NEW IMPORT
from app.schemas.spell import SpellCreate as SpellCreateSchema # <--- NEW IMPORT

# --- Predefined D&D 5e Skills ---
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

# --- Predefined D&D 5e Items (Sample List) ---
# In api/app/db/init_db.py
# Replace the existing PREDEFINED_ITEMS list with this one:

PREDEFINED_ITEMS = [
    # Adventuring Gear
    ItemCreateSchema(name="Backpack", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=2.0, properties={"capacity_lbs": 30, "description": "Holds 1 cubic foot or 30 pounds of gear."}),
    ItemCreateSchema(name="Bedroll", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=7.0, cost_gp=1.0),
    ItemCreateSchema(name="Mess Kit", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.2),
    ItemCreateSchema(name="Tinderbox", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.5, properties={"description": "For lighting fires."}),
    ItemCreateSchema(name="Torch", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.01, properties={"duration_hours": 1, "light_radius_ft": "20 bright, 20 dim"}),
    ItemCreateSchema(name="Rations (1 day)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=2.0, cost_gp=0.5),
    ItemCreateSchema(name="Waterskin", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=0.2, properties={"capacity_gallons": 0.5, "full_weight_lbs": 5}), # Full weight if holding 4 pints of water
    ItemCreateSchema(name="Rope, Hempen (50 feet)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=10.0, cost_gp=1.0),
    ItemCreateSchema(name="Crowbar", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=2.0, properties={"advantage_on_str_checks": "Forcing open doors/chests"}),
    ItemCreateSchema(name="Healer's Kit", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=3.0, cost_gp=5.0, properties={"uses": 10, "action": "Stabilize a creature with 0 HP"}),
    ItemCreateSchema(name="Grappling Hook", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=4.0, cost_gp=2.0),
    ItemCreateSchema(name="Lantern, Hooded", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=2.0, cost_gp=5.0, properties={"light_radius_ft": "30 bright, 30 dim (or 60 dim as hooded)"}),
    ItemCreateSchema(name="Oil (flask)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.1, properties={"use": "Fuel for lantern (6 hours), or can be thrown (5ft radius fire, 1 min)"}),
    ItemCreateSchema(name="Quiver", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=1.0, properties={"capacity": "Holds 20 arrows"}),
    ItemCreateSchema(name="Arrows (20)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=1.0), # Ammunition, often tracked with weapons

    # Tools
    ItemCreateSchema(name="Thieves' Tools", item_type=ItemTypeEnum.TOOL, weight=1.0, cost_gp=25.0, properties={"use": "Disarm traps, open locks"}),
    ItemCreateSchema(name="Herbalism Kit", item_type=ItemTypeEnum.TOOL, weight=3.0, cost_gp=5.0, properties={"use": "Create antitoxin, potions of healing"}),
    ItemCreateSchema(name="Lute", item_type=ItemTypeEnum.TOOL, weight=2.0, cost_gp=35.0, properties={"type": "Musical Instrument"}),
    ItemCreateSchema(name="Drum", item_type=ItemTypeEnum.TOOL, weight=3.0, cost_gp=6.0, properties={"type": "Musical Instrument"}),
    ItemCreateSchema(name="Playing Card Set", item_type=ItemTypeEnum.TOOL, weight=0.0, cost_gp=0.5, properties={"type": "Gaming Set"}), # Weight negligible
    ItemCreateSchema(name="Dice Set", item_type=ItemTypeEnum.TOOL, weight=0.0, cost_gp=0.1, properties={"type": "Gaming Set"}), # Weight negligible
    ItemCreateSchema(name="Spellbook (Blank)", item_type=ItemTypeEnum.TOOL, weight=3.0, cost_gp=50.0, properties={"description": "A blank spellbook for wizards."}),


    # Weapons (Simple Melee)
    ItemCreateSchema(name="Club", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=0.1, properties={"damage": "1d4 bludgeoning", "type": "simple melee", "properties": ["light"]}),
    ItemCreateSchema(name="Dagger", item_type=ItemTypeEnum.WEAPON, weight=1.0, cost_gp=2.0, properties={"damage": "1d4 piercing", "type": "simple melee", "properties": ["finesse", "light", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Greatclub", item_type=ItemTypeEnum.WEAPON, weight=10.0, cost_gp=0.2, properties={"damage": "1d8 bludgeoning", "type": "simple melee", "properties": ["two-handed"]}),
    ItemCreateSchema(name="Handaxe", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=5.0, properties={"damage": "1d6 slashing", "type": "simple melee", "properties": ["light", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Javelin", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=0.5, properties={"damage": "1d6 piercing", "type": "simple melee", "properties": ["thrown (range 30/120)"]}),
    ItemCreateSchema(name="Light Hammer", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=2.0, properties={"damage": "1d4 bludgeoning", "type": "simple melee", "properties": ["light", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Mace", item_type=ItemTypeEnum.WEAPON, weight=4.0, cost_gp=5.0, properties={"damage": "1d6 bludgeoning", "type": "simple melee", "properties": []}),
    ItemCreateSchema(name="Quarterstaff", item_type=ItemTypeEnum.WEAPON, weight=4.0, cost_gp=0.2, properties={"damage": "1d6 bludgeoning", "type": "simple melee", "properties": ["versatile (1d8)"]}),
    ItemCreateSchema(name="Sickle", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=1.0, properties={"damage": "1d4 slashing", "type": "simple melee", "properties": ["light"]}),
    ItemCreateSchema(name="Spear", item_type=ItemTypeEnum.WEAPON, weight=3.0, cost_gp=1.0, properties={"damage": "1d6 piercing", "type": "simple melee", "properties": ["thrown (range 20/60)", "versatile (1d8)"]}),

    # Weapons (Simple Ranged)
    ItemCreateSchema(name="Light Crossbow", item_type=ItemTypeEnum.WEAPON, weight=5.0, cost_gp=25.0, properties={"damage": "1d8 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "loading", "two-handed"]}),
    ItemCreateSchema(name="Dart", item_type=ItemTypeEnum.WEAPON, weight=0.25, cost_gp=0.05, properties={"damage": "1d4 piercing", "type": "simple ranged", "properties": ["finesse", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Shortbow", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=25.0, properties={"damage": "1d6 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "two-handed"]}),
    ItemCreateSchema(name="Sling", item_type=ItemTypeEnum.WEAPON, weight=0.0, cost_gp=0.1, properties={"damage": "1d4 bludgeoning", "type": "simple ranged", "properties": ["ammunition (range 30/120)"]}), # Weight negligible

    # Weapons (Martial Melee)
    ItemCreateSchema(name="Battleaxe", item_type=ItemTypeEnum.WEAPON, weight=4.0, cost_gp=10.0, properties={"damage": "1d8 slashing", "type": "martial melee", "properties": ["versatile (1d10)"]}),
    ItemCreateSchema(name="Longsword", item_type=ItemTypeEnum.WEAPON, weight=3.0, cost_gp=15.0, properties={"damage": "1d8 slashing", "type": "martial melee", "properties": ["versatile (1d10)"]}),
    ItemCreateSchema(name="Rapier", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=25.0, properties={"damage": "1d8 piercing", "type": "martial melee", "properties": ["finesse"]}),
    ItemCreateSchema(name="Scimitar", item_type=ItemTypeEnum.WEAPON, weight=3.0, cost_gp=25.0, properties={"damage": "1d6 slashing", "type": "martial melee", "properties": ["finesse", "light"]}),
    ItemCreateSchema(name="Shortsword", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=10.0, properties={"damage": "1d6 piercing", "type": "martial melee", "properties": ["finesse", "light"]}),
    ItemCreateSchema(name="Warhammer", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=15.0, properties={"damage": "1d8 bludgeoning", "type": "martial melee", "properties": ["versatile (1d10)"]}),
    
    # Weapons (Martial Ranged)
    ItemCreateSchema(name="Longbow", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=50.0, properties={"damage": "1d8 piercing", "type": "martial ranged", "properties": ["ammunition (range 150/600)", "heavy", "two-handed"]}),

    # Armor
    ItemCreateSchema(name="Padded Armor", item_type=ItemTypeEnum.ARMOR, weight=8.0, cost_gp=5.0, properties={"ac_base": 11, "armor_type": "light", "dex_bonus": True, "stealth_disadvantage": True}),
    ItemCreateSchema(name="Leather Armor", item_type=ItemTypeEnum.ARMOR, weight=10.0, cost_gp=10.0, properties={"ac_base": 11, "armor_type": "light", "dex_bonus": True, "stealth_disadvantage": False}),
    ItemCreateSchema(name="Studded Leather Armor", item_type=ItemTypeEnum.ARMOR, weight=13.0, cost_gp=45.0, properties={"ac_base": 12, "armor_type": "light", "dex_bonus": True, "stealth_disadvantage": False}),
    ItemCreateSchema(name="Chain Shirt", item_type=ItemTypeEnum.ARMOR, weight=20.0, cost_gp=50.0, properties={"ac_base": 13, "armor_type": "medium", "dex_bonus": True, "dex_bonus_max": 2, "stealth_disadvantage": False}),
    ItemCreateSchema(name="Scale Mail", item_type=ItemTypeEnum.ARMOR, weight=45.0, cost_gp=50.0, properties={"ac_base": 14, "armor_type": "medium", "dex_bonus": True, "dex_bonus_max": 2, "stealth_disadvantage": True}),
    ItemCreateSchema(name="Plate Armor", item_type=ItemTypeEnum.ARMOR, weight=65.0, cost_gp=1500.0, properties={"ac_base": 18, "armor_type": "heavy", "dex_bonus": False, "strength_requirement": 15, "stealth_disadvantage": True}),
    ItemCreateSchema(name="Shield", item_type=ItemTypeEnum.SHIELD, weight=6.0, cost_gp=10.0, properties={"ac_bonus": 2}),

    # Potions
    ItemCreateSchema(name="Potion of Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=50.0, properties={"effect": "Restores 2d4+2 hit points."}),
    ItemCreateSchema(name="Potion of Greater Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=250.0, properties={"effect": "Restores 4d4+4 hit points."}), # Cost is an estimate
]

# --- Predefined D&D 5e Spells (Sample List) ---
PREDEFINED_SPELLS = [
    SpellCreateSchema(
        name="Magic Missile",
        description="You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range. A dart deals 1d4 + 1 force damage to its target. The darts all strike simultaneously, and you can direct them to hit one creature or several.",
        higher_level="When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st.",
        range="120 feet",
        components="V, S",
        material=None,
        ritual=False,
        duration="Instantaneous",
        concentration=False,
        casting_time="1 action",
        level=1,
        school=SchoolOfMagicEnum.EVOCATION,
        dnd_classes=["Sorcerer", "Wizard"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Fireball",
        description="A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one. The fire spreads around corners. It ignites flammable objects in the area that aren’t being worn or carried.",
        higher_level="When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.",
        range="150 feet",
        components="V, S, M",
        material="A tiny ball of bat guano and sulfur.",
        ritual=False,
        duration="Instantaneous",
        concentration=False,
        casting_time="1 action",
        level=3,
        school=SchoolOfMagicEnum.EVOCATION,
        dnd_classes=["Sorcerer", "Wizard"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Cure Wounds",
        description="A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.",
        higher_level="When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d8 for each slot level above 1st.",
        range="Touch",
        components="V, S",
        material=None,
        ritual=False,
        duration="Instantaneous",
        concentration=False,
        casting_time="1 action",
        level=1,
        school=SchoolOfMagicEnum.EVOCATION, # SRD lists it as Evocation, some prefer Conjuration (healing)
        dnd_classes=["Bard", "Cleric", "Druid", "Paladin", "Ranger"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Mage Armor",
        description="You touch a willing creature who isn’t wearing armor, and a protective magical force surrounds it until the spell ends. The target’s base AC becomes 13 + its Dexterity modifier. The spell ends if the target dons armor or if you dismiss the spell as an action.",
        higher_level=None,
        range="Touch",
        components="V, S, M",
        material="A piece of cured leather.",
        ritual=False,
        duration="8 hours",
        concentration=False,
        casting_time="1 action",
        level=1,
        school=SchoolOfMagicEnum.ABJURATION,
        dnd_classes=["Sorcerer", "Wizard"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Light", # Cantrip
        description="You touch one object that is no larger than 10 feet in any dimension. Until the spell ends, the object sheds bright light in a 20-foot radius and dim light for an additional 20 feet. The light can be colored as you like. Completely covering the object with something opaque blocks the light. The spell ends if you cast it again or dismiss it as an action.",
        higher_level=None,
        range="Touch",
        components="V, M",
        material="A firefly or phosphorescent moss.",
        ritual=False,
        duration="1 hour",
        concentration=False,
        casting_time="1 action",
        level=0, # Cantrip
        school=SchoolOfMagicEnum.EVOCATION,
        dnd_classes=["Bard", "Cleric", "Sorcerer", "Wizard"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Shield",
        description="An invisible barrier of magical force appears and protects you. Until the start of your next turn, you have a +5 bonus to AC, including against the triggering attack, and you take no damage from magic missile.",
        higher_level=None,
        range="Self",
        components="V, S",
        material=None,
        ritual=False,
        duration="1 round",
        concentration=False,
        casting_time="1 reaction, which you take when you are hit by an attack or targeted by the magic missile spell",
        level=1,
        school=SchoolOfMagicEnum.ABJURATION,
        dnd_classes=["Sorcerer", "Wizard"],
        source_book="SRD"
    ),
    SpellCreateSchema(
        name="Bless",
        description="You bless up to three creatures of your choice within range. Whenever a target makes an attack roll or a saving throw before the spell ends, the target can roll a d4 and add the number rolled to the attack roll or saving throw.",
        higher_level="When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.",
        range="30 feet",
        components="V, S, M",
        material="A sprinkling of holy water.",
        ritual=False,
        duration="Concentration, up to 1 minute",
        concentration=True,
        casting_time="1 action",
        level=1,
        school=SchoolOfMagicEnum.ENCHANTMENT, # SRD lists as enchantment
        dnd_classes=["Cleric", "Paladin"],
        source_book="SRD"
    )
]

async def seed_skills(db: AsyncSession) -> None:
    print("Attempting to seed skills...")
    skills_added_in_this_run = 0
    for skill_data in PREDEFINED_SKILLS:
        result = await db.execute(select(SkillModel).filter(SkillModel.name == skill_data.name))
        existing_skill = result.scalars().first()

        if not existing_skill:
            db_skill = SkillModel(
                name=skill_data.name,
                ability_modifier_name=skill_data.ability_modifier_name,
                description=skill_data.description
            )
            db.add(db_skill)
            print(f"Adding skill: {skill_data.name}")
            skills_added_in_this_run += 1

    if skills_added_in_this_run > 0:
        try:
            await db.commit()
            print(f"Successfully added {skills_added_in_this_run} new skills and committed.")
        except Exception as e:
            await db.rollback()
            print(f"Error during skill seeding commit: {e}")
    else:
        print("No new skills to add. Database skill list appears up to date.")


# --- NEW SEEDING FUNCTION FOR ITEMS ---
async def seed_items(db: AsyncSession) -> None:
    print("Attempting to seed items...")
    items_added_in_this_run = 0
    for item_data in PREDEFINED_ITEMS:
        # Check if item already exists by name
        result = await db.execute(select(ItemModel).filter(ItemModel.name == item_data.name))
        existing_item = result.scalars().first()

        if not existing_item:
            db_item = ItemModel(
                name=item_data.name,
                description=item_data.description,
                item_type=item_data.item_type,
                weight=item_data.weight,
                cost_gp=item_data.cost_gp,
                properties=item_data.properties
            )
            db.add(db_item)
            print(f"Adding item: {item_data.name}")
            items_added_in_this_run += 1
        # else:
            # print(f"Item already exists: {item_data.name}") # Optional: can be noisy

    if items_added_in_this_run > 0:
        try:
            await db.commit() # Commit after attempting to add all new items
            print(f"Successfully added {items_added_in_this_run} new items and committed.")
        except Exception as e:
            await db.rollback()
            print(f"Error during item seeding commit: {e}")
    else:
        print("No new items to add. Database item list appears up to date.")

# --- NEW SEEDING FUNCTION FOR SPELLS ---
async def seed_spells(db: AsyncSession) -> None:
    print("Attempting to seed spells...")
    spells_added_in_this_run = 0
    for spell_data in PREDEFINED_SPELLS:
        # Check if spell already exists by name
        result = await db.execute(select(SpellModel).filter(SpellModel.name == spell_data.name))
        existing_spell = result.scalars().first()

        if not existing_spell:
            # Create the SpellModel instance from the SpellCreateSchema
            # The schema 'dnd_classes' is List[str], model 'dnd_classes' is JSON.
            # Pydantic's model_dump() will handle this conversion appropriately if model is configured for it.
            # Or, ensure that the model can take List[str] and it gets serialized to JSON by SQLAlchemy.
            # Our Spell model's dnd_classes = Column(JSON, nullable=True) should handle dict/list from Pydantic.
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
                dnd_classes=spell_data.dnd_classes, # Pydantic schema has List[str], model has JSON
                source_book=spell_data.source_book
            )
            db.add(db_spell)
            print(f"Adding spell: {spell_data.name}")
            spells_added_in_this_run += 1
        # else:
            # print(f"Spell already exists: {spell_data.name}") # Optional

    if spells_added_in_this_run > 0:
        try:
            await db.commit() # Commit after attempting to add all new spells
            print(f"Successfully added {spells_added_in_this_run} new spells and committed.")
        except Exception as e:
            await db.rollback()
            print(f"Error during spell seeding commit: {e}")
    else:
        print("No new spells to add. Database spell list appears up to date.")
