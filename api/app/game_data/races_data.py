# Path: api/app/game_data/races_data.py

# This list contains predefined race data based on SRD 5.1, including subraces.
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
        ],
        "subraces": [
            {
                "name": "Hill Dwarf",
                "ability_score_increase": {"wisdom": 1},
                "racial_traits": [
                    {"name": "Dwarven Toughness", "desc": "Your hit point maximum increases by 1, and it increases by 1 every time you gain a level."}
                ]
            },
            {
                "name": "Mountain Dwarf",
                "ability_score_increase": {"strength": 2},
                "racial_traits": [
                    {"name": "Dwarven Armor Training", "desc": "You have proficiency with light and medium armor."}
                ]
            }
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
            {"name": "Darkvision", "desc": "Accustomed to twilit forests and the night sky, you have superior vision in dark and dim conditions."},
            {"name": "Keen Senses", "desc": "You have proficiency in the Perception skill."},
            {"name": "Fey Ancestry", "desc": "You have advantage on saving throws against being charmed, and magic can't put you to sleep."},
            {"name": "Trance", "desc": "Elves don't need to sleep. Instead, they meditate deeply, remaining semiconscious, for 4 hours a day."}
        ],
        "subraces": [
            {
                "name": "High Elf",
                "ability_score_increase": {"intelligence": 1},
                "racial_traits": [
                    {"name": "Elf Weapon Training", "desc": "You have proficiency with the longsword, shortsword, shortbow, and longbow."},
                    {"name": "Cantrip", "desc": "You know one cantrip of your choice from the wizard spell list. Intelligence is your spellcasting ability for it."},
                    {"name": "Extra Language", "desc": "You can speak, read, and write one extra language of your choice."}
                ]
            },
            {
                "name": "Wood Elf",
                "ability_score_increase": {"wisdom": 1},
                "racial_traits": [
                    {"name": "Elf Weapon Training", "desc": "You have proficiency with the longsword, shortsword, shortbow, and longbow."},
                    {"name": "Fleet of Foot", "desc": "Your base walking speed increases to 35 feet."},
                    {"name": "Mask of the Wild", "desc": "You can attempt to hide even when you are only lightly obscured by foliage, heavy rain, falling snow, mist, and other natural phenomena."}
                ]
            },
            {
                "name": "Drow (Dark Elf)",
                "ability_score_increase": {"charisma": 1},
                "racial_traits": [
                    {"name": "Superior Darkvision", "desc": "Your darkvision has a radius of 120 feet."},
                    {"name": "Sunlight Sensitivity", "desc": "You have disadvantage on attack rolls and on Wisdom (Perception) checks that rely on sight when you, the target of your attack, or whatever you are trying to perceive is in direct sunlight."},
                    {"name": "Drow Magic", "desc": "You know the dancing lights cantrip. When you reach 3rd level, you can cast the faerie fire spell once per day. When you reach 5th level, you can also cast the darkness spell once per day. Charisma is your spellcasting ability for these spells."},
                    {"name": "Drow Weapon Training", "desc": "You have proficiency with rapiers, shortswords, and hand crossbows."}
                ]
            }
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
        ],
        "subraces": [
            {
                "name": "Lightfoot",
                "ability_score_increase": {"charisma": 1},
                "racial_traits": [
                    {"name": "Naturally Stealthy", "desc": "You can attempt to hide even when you are obscured only by a creature that is at least one size larger than you."}
                ]
            },
            {
                "name": "Stout",
                "ability_score_increase": {"constitution": 1},
                "racial_traits": [
                    {"name": "Stout Resilience", "desc": "You have advantage on saving throws against poison, and you have resistance against poison damage."}
                ]
            }
        ]
    },
    {
        "name": "Human",
        "description": "Humans are the most adaptable and ambitious people among the common races. Whatever drives them, humans are the innovators, the achievers, and the pioneers of the worlds.",
        "ability_score_increase": {"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, and one extra language of your choice",
        "racial_traits": [],
        "subraces": []
    },
    {
        "name": "Dragonborn",
        "description": "Born of dragons, as their name proclaims, dragonborn walk proudly through a world that greets them with fearful incomprehension.",
        "ability_score_increase": {"strength": 2, "charisma": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Draconic",
        "racial_traits": [
            {"name": "Draconic Ancestry", "desc": "You have draconic ancestry. Choose one type of dragon from the Draconic Ancestry table. Your breath weapon and damage resistance are determined by the dragon type."},
            {"name": "Breath Weapon", "desc": "You can use your action to exhale destructive energy."},
            {"name": "Damage Resistance", "desc": "You have resistance to the damage type associated with your draconic ancestry."}
        ],
        "subraces": []
    },
    {
        "name": "Gnome",
        "description": "A gnome's energy and enthusiasm for living shines through every inch of his or her tiny body.",
        "ability_score_increase": {"intelligence": 2},
        "size": "Small",
        "speed": 25,
        "languages": "Common, Gnomish",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Accustomed to life underground, you have superior vision in dark and dim conditions."},
            {"name": "Gnome Cunning", "desc": "You have advantage on all Intelligence, Wisdom, and Charisma saving throws against magic."}
        ],
        "subraces": [
            {
                "name": "Rock Gnome",
                "ability_score_increase": {"constitution": 1},
                "racial_traits": [
                    {"name": "Artificer's Lore", "desc": "Whenever you make an Intelligence (History) check related to magic items, alchemical objects, or technological devices, you can add twice your proficiency bonus, instead of any proficiency bonus you normally apply."},
                    {"name": "Tinker", "desc": "You have proficiency with artisan's tools (tinker's tools). Using those tools, you can spend 1 hour and 10 gp worth of materials to construct a Tiny clockwork device (AC 5, 1 hp)."}
                ]
            },
            {
                "name": "Forest Gnome",
                "ability_score_increase": {"dexterity": 1},
                "racial_traits": [
                    {"name": "Natural Illusionist", "desc": "You know the minor illusion cantrip. Intelligence is your spellcasting ability for it."},
                    {"name": "Speak with Small Beasts", "desc": "Through sounds and gestures, you can communicate simple ideas with Small or smaller beasts."}
                ]
            }
        ]
    },
    {
        "name": "Half-Elf",
        "description": "Walking in two worlds but truly belonging to neither, half-elves combine what some say are the best qualities of their elf and human parents. Their Charisma score increases by 2, and two other ability scores of their choice increase by 1.",
        "ability_score_increase": {"charisma": 2},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Elvish, and one extra language of your choice",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your elf blood, you have superior vision in dark and dim conditions."},
            {"name": "Fey Ancestry", "desc": "You have advantage on saving throws against being charmed, and magic can't put you to sleep."},
            {"name": "Skill Versatility", "desc": "You gain proficiency in two skills of your choice."}
        ],
        "subraces": []
    },
    {
        "name": "Half-Orc",
        "description": "Whether united under the leadership of a powerful warlock or having fought their way out of servitude, half-orcs must be strong to survive.",
        "ability_score_increase": {"strength": 2, "constitution": 1},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Orc",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your orc blood, you have superior vision in dark and dim conditions."},
            {"name": "Menacing", "desc": "You gain proficiency in the Intimidation skill."},
            {"name": "Relentless Endurance", "desc": "When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead. You can’t use this feature again until you finish a long rest."},
            {"name": "Savage Attacks", "desc": "When you score a critical hit with a melee weapon attack, you can roll one of the weapon's damage dice one additional time and add it to the extra damage of the critical hit."}
        ],
        "subraces": []
    },
    {
        "name": "Tiefling",
        "description": "To be greeted with stares and whispers, to suffer violence and insult on the street, to see mistrust and fear in every eye: this is the lot of the tiefling.",
        "ability_score_increase": {"intelligence": 1, "charisma": 2},
        "size": "Medium",
        "speed": 30,
        "languages": "Common, Infernal",
        "racial_traits": [
            {"name": "Darkvision", "desc": "Thanks to your infernal heritage, you have superior vision in dark and dim conditions."},
            {"name": "Hellish Resistance", "desc": "You have resistance to fire damage."},
            {"name": "Infernal Legacy", "desc": "You know the thaumaturgy cantrip. Once you reach 3rd level, you can cast the hellish rebuke spell once per day as a 2nd-level spell. Once you reach 5th level, you can also cast the darkness spell once per day. Charisma is your spellcasting ability for these spells."}
        ],
        "subraces": []
    }
]
