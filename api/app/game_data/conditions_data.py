# Path: api/app/game_data/conditions_data.py

# This list contains predefined condition data based on SRD 5.1.
# The data is structured as simple dictionaries to be validated by the seeder.
PREDEFINED_CONDITIONS = [
    {
        "name": "Blinded",
        "description": "- A blinded creature can't see and automatically fails any ability check that requires sight.\n- Attack rolls against the creature have advantage, and the creature's attack rolls have disadvantage."
    },
    {
        "name": "Charmed",
        "description": "- A charmed creature can't attack the charmer or target the charmer with harmful abilities or magical effects.\n- The charmer has advantage on any ability check to interact socially with the creature."
    },
    {
        "name": "Deafened",
        "description": "- A deafened creature can't hear and automatically fails any ability check that requires hearing."
    },
    {
        "name": "Frightened",
        "description": "- A frightened creature has disadvantage on ability checks and attack rolls while the source of its fear is within line of sight.\n- The creature can't willingly move closer to the source of its fear."
    },
    {
        "name": "Grappled",
        "description": "- A grappled creature's speed becomes 0, and it can't benefit from any bonus to its speed.\n- The condition ends if the grappler is incapacitated.\n- The condition also ends if an effect removes the grappled creature from the reach of the grappler or grappling effect, such as when a creature is hurled away by the thunderwave spell."
    },
    {
        "name": "Incapacitated",
        "description": "- An incapacitated creature can't take actions or reactions."
    },
    {
        "name": "Invisible",
        "description": "- An invisible creature is impossible to see without the aid of magic or a special sense. For the purpose of hiding, the creature is heavily obscured.\n- The creature's location can be detected by any noise it makes or any tracks it leaves.\n- Attack rolls against the creature have disadvantage, and the creature's attack rolls have advantage."
    },
    {
        "name": "Paralyzed",
        "description": "- A paralyzed creature is incapacitated and can't move or speak.\n- The creature automatically fails Strength and Dexterity saving throws.\n- Attack rolls against the creature have advantage.\n- Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature."
    },
    {
        "name": "Petrified",
        "description": "- A petrified creature is transformed, along with any nonmagical object it is wearing or carrying, into a solid inanimate substance (usually stone).\n- Its weight increases by a factor of ten, and it ceases aging.\n- The creature is incapacitated, can't move or speak, and is unaware of its surroundings.\n- Attack rolls against the creature have advantage.\n- The creature automatically fails Strength and Dexterity saving throws.\n- The creature has resistance to all damage.\n- The creature is immune to poison and disease, though a poison or disease already in its system is suspended, not neutralized."
    },
    {
        "name": "Poisoned",
        "description": "- A poisoned creature has disadvantage on attack rolls and ability checks."
    },
    {
        "name": "Prone",
        "description": "- A prone creature's only movement option is to crawl, unless it stands up and thereby ends the condition.\n- The creature has disadvantage on attack rolls.\n- An attack roll against the creature has advantage if the attacker is within 5 feet of the creature. Otherwise, the attack roll has disadvantage."
    },
    {
        "name": "Restrained",
        "description": "- A restrained creature's speed becomes 0, and it can't benefit from any bonus to its speed.\n- Attack rolls against the creature have advantage, and the creature's attack rolls have disadvantage.\n- The creature has disadvantage on Dexterity saving throws."
    },
    {
        "name": "Stunned",
        "description": "- A stunned creature is incapacitated, can't move, and can speak only falteringly.\n- The creature automatically fails Strength and Dexterity saving throws.\n- Attack rolls against the creature have advantage."
    },
    {
        "name": "Unconscious",
        "description": "- An unconscious creature is incapacitated, can't move or speak, and is unaware of its surroundings.\n- The creature drops whatever it's holding and falls prone.\n- The creature automatically fails Strength and Dexterity saving throws.\n- Attack rolls against the creature have advantage.\n- Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature."
    }
]