from app.schemas.monster import MonsterCreate as MonsterCreateSchema
from app.models.monster import Monster as MonsterMode

PREDEFINED_MONSTERS = [
    {
        "name": "Goblin", "size": "Small", "creature_type": "humanoid (goblinoid)", "alignment": "neutral evil",
        "armor_class": 15, "hit_points": 7, "hit_dice": "2d6",
        "speed": {"walk": "30 ft."},
        "strength": 8, "dexterity": 14, "constitution": 10, "intelligence": 10, "wisdom": 8, "charisma": 8,
        "proficiencies": [{"proficiency": {"name": "Stealth"}, "value": 6}],
        "damage_vulnerabilities": [], "damage_resistances": [], "damage_immunities": [], "condition_immunities": [],
        "senses": {"darkvision": "60 ft.", "passive_perception": 9},
        "languages": "Common, Goblin", "challenge_rating": 0.25, "xp": 50,
        "special_abilities": [{"name": "Nimble Escape", "desc": "The goblin can take the Disengage or Hide action as a bonus action on each of its turns."}],
        "actions": [{"name": "Scimitar", "desc": "Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 5 (1d6 + 2) slashing damage."}, {"name": "Shortbow", "desc": "Ranged Weapon Attack: +4 to hit, range 80/320 ft., one target. Hit: 5 (1d6 + 2) piercing damage."}]
    },
    {
        "name": "Orc", "size": "Medium", "creature_type": "humanoid (orc)", "alignment": "chaotic evil",
        "armor_class": 13, "hit_points": 15, "hit_dice": "2d8 + 6",
        "speed": {"walk": "30 ft."},
        "strength": 16, "dexterity": 12, "constitution": 16, "intelligence": 7, "wisdom": 11, "charisma": 10,
        "proficiencies": [{"proficiency": {"name": "Intimidation"}, "value": 2}],
        "damage_vulnerabilities": [], "damage_resistances": [], "damage_immunities": [], "condition_immunities": [],
        "senses": {"darkvision": "60 ft.", "passive_perception": 10},
        "languages": "Common, Orc", "challenge_rating": 0.5, "xp": 100,
        "special_abilities": [{"name": "Aggressive", "desc": "As a bonus action on its turn, the orc can move up to its speed toward a hostile creature that it can see."}],
        "actions": [{"name": "Greataxe", "desc": "Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 9 (1d12 + 3) slashing damage."}, {"name": "Javelin", "desc": "Melee or Ranged Weapon Attack: +5 to hit, reach 5 ft. or range 30/120 ft., one target. Hit: 6 (1d6 + 3) piercing damage."}]
    },
    {
        "name": "Skeleton", "size": "Medium", "creature_type": "undead", "alignment": "lawful evil",
        "armor_class": 13, "hit_points": 13, "hit_dice": "2d8 + 4",
        "speed": {"walk": "30 ft."},
        "strength": 10, "dexterity": 14, "constitution": 15, "intelligence": 6, "wisdom": 8, "charisma": 5,
        "proficiencies": [],
        "damage_vulnerabilities": ["bludgeoning"], "damage_resistances": [], "damage_immunities": ["poison"], "condition_immunities": ["exhaustion", "poisoned"],
        "senses": {"darkvision": "60 ft.", "passive_perception": 9},
        "languages": "understands all languages it knew in life but can't speak", "challenge_rating": 0.25, "xp": 50,
        "special_abilities": [],
        "actions": [{"name": "Shortsword", "desc": "Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 5 (1d6 + 2) piercing damage."}, {"name": "Shortbow", "desc": "Ranged Weapon Attack: +4 to hit, range 80/320 ft., one target. Hit: 5 (1d6 + 2) piercing damage."}]
    }
]
