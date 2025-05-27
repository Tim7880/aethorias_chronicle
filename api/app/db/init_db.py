# Path: api/app/db/init_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.skill import Skill as SkillModel
from app.schemas.skill import SkillCreate as SkillCreateSchema # For structured data
# from app.crud import crud_skill # We will create this crud_skill.py file next or add to existing

# Predefined D&D 5e Skills
# (Descriptions are optional and can be added or kept brief)
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

async def seed_skills(db: AsyncSession) -> None:
    """
    Populates the skills table with predefined D&D 5e skills if they don't already exist.
    """
    print("Attempting to seed skills...")
    for skill_data in PREDEFINED_SKILLS:
        # Check if skill already exists
        result = await db.execute(select(SkillModel).filter(SkillModel.name == skill_data.name))
        existing_skill = result.scalars().first()

        if not existing_skill:
            # If we had a crud_skill.create_skill function, we'd use it.
            # For now, let's create directly or assume crud_skill will be simple.
            # This is a simplified direct creation for seeding:
            db_skill = SkillModel(
                name=skill_data.name,
                ability_modifier_name=skill_data.ability_modifier_name,
                description=skill_data.description
            )
            db.add(db_skill)
            print(f"Adding skill: {skill_data.name}")
        else:
            print(f"Skill already exists: {skill_data.name}")

    # Only commit if changes were made (though committing an empty transaction is usually harmless)
    # For simplicity in seeding, we can just commit.
    try:
        await db.commit()
        print("Skills seeding committed.")
    except Exception as e:
        await db.rollback()
        print(f"Error during skill seeding commit: {e}")