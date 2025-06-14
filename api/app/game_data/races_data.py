# Path: api/app/game_data/races_data.py

# This list contains predefined race data based on SRD 5.1
# Note: Pydantic schemas are not used here to avoid circular imports and keep data pure.
# The seeding script will handle validation.
PREDEFINED_RACES = [
    {
        "name": "Dwarf",
        "description": "Bold and hardy, dwarves are known as skilled warriors, miners, and workers of stone and metal.",
        "ability_score_increase": {"constitution": 2},
        "size": "Medium",
        "speed": 25,
        "languages": "Common, Dwarvish",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Accustomed to life underground, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Dwarven Resilience", "desc": "You have advantage on saving throws against poison, and you have resistance against poison damage."},
            {"name": "Dwarven Combat Training", "desc": "You have proficiency with the battleaxe, handaxe, light hammer, and warhammer."},
            {"name": "Tool Proficiency", "desc": "You gain proficiency with the artisan's tools of your choice: smith's tools, brewer's supplies, or mason's tools."},
            {"name": "Stonecunning", "desc": "Whenever you make an Intelligence (History) check related to the origin of stonework, you are considered proficient in the History skill and add double your proficiency bonus to the check, instead of your normal proficiency bonus."}
        ]
    },
    {
        "name": "Elf",
        "description": "Elves are a magical people of otherworldly grace, living in the world but not entirely part of it.",
        "ability_score_increase": {"dexterity": 2},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Elvish",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Accustomed to twilit forests and the night sky, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Keen Senses", "desc": "You have proficiency in the Perception skill."},
            {"name": "Fey Ancestry", "desc": "You have advantage on saving throws against being charmed, and magic can't put you to sleep."},
            {"name": "Trance", "desc": "Elves don't need to sleep. Instead, they meditate deeply, remaining semiconscious, for 4 hours a day. After resting in this way, you gain the same benefit that a human does from 8 hours of sleep."}
        ]
    },
    {
        "name": "Halfling",
        "description": "The comforts of home are the goals of most halflings' lives: a place to settle in peace and quiet, far from marauding monsters and clashing armies.",
        "ability_score_increase": {"dexterity": 2},
        "size": "Small",
        "speed": 25,
        "languages": "Common, Halfling",
        "racial_traits": [
            {"name": "Lucky", "desc": "When you roll a 1 on an attack roll, ability check, or saving throw, you can reroll the die and must use the new roll."},
            {"name": "Brave", "desc": "You have advantage on saving throws against being frightened."},
            {"name": "Halfling Nimbleness", "desc": "You can move through the space of any creature that is of a size larger than yours."}
        ]
    },
    {
        "name": "Human",
        "description": "Humans are the most adaptable and ambitious people among the common races. Whatever drives them, humans are the innovators, the achievers, and the pioneers of the worlds.",
        "ability_score_increase": {"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, one extra language of your choice",
        "racial_traits": []
    },
    {
        "name": "Dragonborn",
        "description": "Born of dragons, as their name proclaims, dragonborn walk proudly through a world that greets them with fearful incomprehension.",
        "ability_score_increase": {"strength": 2, "charisma": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Draconic",
        "racial_traits": [
            {"name": "Draconic Ancestry", "desc": "You have draconic ancestry. Choose one type of dragon from the Draconic Ancestry table. Your breath weapon and damage resistance are determined by the dragon type, as shown in the table."},
            {"name": "Breath Weapon", "desc": "You can use your action to exhale destructive energy. Your draconic ancestry determines the size, shape, and damage type of the exhalation."},
            {"name": "Damage Resistance", "desc": "You have resistance to the damage type associated with your draconic ancestry."}
        ]
    },
    {
        "name": "Gnome",
        "description": "A gnome's energy and enthusiasm for living shines through every inch of his or her tiny body.",
        "ability_score_increase": {"intelligence": 2},
        "size": "Small",
        "speed": 25,
        "languages": "Common, Gnomish",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Accustomed to life underground, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Gnome Cunning", "desc": "You have advantage on all Intelligence, Wisdom, and Charisma saving throws against magic."}
        ]
    },
    {
        "name": "Half-Elf",
        "description": "Walking in two worlds but truly belonging to neither, half-elves combine what some say are the best qualities of their elf and human parents. Their Charisma score increases by 2, and two other ability scores of their choice increase by 1.",
        # --- START MODIFICATION ---
        "ability_score_increase": {"charisma": 2},
        # --- END MODIFICATION ---
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Elvish, and one extra language of your choice",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your elf blood, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Fey Ancestry", "desc": "You have advantage on saving throws against being charmed, and magic can't put you to sleep."},
            {"name": "Skill Versatility", "desc": "You gain proficiency in two skills of your choice."}
        ]
    },
    {
        "name": "Half-Orc",
        "description": "Whether united under the leadership of a powerful warlock or having fought their way out of servitude, half-orcs must be strong to survive.",
        "ability_score_increase": {"strength": 2, "constitution": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Orc",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your orc blood, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Menacing", "desc": "You gain proficiency in the Intimidation skill."},
            {"name": "Relentless Endurance", "desc": "When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead. You can’t use this feature again until you finish a long rest."},
            {"name": "Savage Attacks", "desc": "When you score a critical hit with a melee weapon attack, you can roll one of the weapon's damage dice one additional time and add it to the extra damage of the critical hit."}
        ]
    },
    {
        "name": "Tiefling",
        "description": "To be greeted with stares and whispers, to suffer violence and insult on the street, to see mistrust and fear in every eye: this is the lot of the tiefling.",
        "ability_score_increase": {"intelligence": 1, "charisma": 2},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Infernal",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your infernal heritage, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light."},
            {"name": "Hellish Resistance", "desc": "You have resistance to fire damage."},
            {"name": "Infernal Legacy", "desc": "You know the thaumaturgy cantrip. Once you reach 3rd level, you can cast the hellish rebuke spell once per day as a 2nd-level spell. Once you reach 5th level, you can also cast the darkness spell once per day. Charisma is your spellcasting ability for these spells."}
        ]
    }
]
