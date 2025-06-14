from app.schemas.dnd_class import DndClassCreate, ClassLevelCreate
from app.models.dnd_class import DndClass as DndClassModel, ClassLevel as ClassLevelModel 


PREDEFINED_CLASSES_DATA = [
    {
        "class_data": {
            "name": "Rogue", 
            "description": "A scoundrel who uses stealth and trickery to overcome obstacles and enemies.", 
            "hit_die": 8
        },
        "levels": [
            {"level": 1, "proficiency_bonus": 2, "features": [{"name": "Expertise"}, {"name": "Sneak Attack (1d6)"}, {"name": "Thieves' Cant"}]},
            {"level": 2, "proficiency_bonus": 2, "features": [{"name": "Cunning Action"}]},
            {"level": 3, "proficiency_bonus": 2, "features": [{"name": "Roguish Archetype"}, {"name": "Sneak Attack (2d6)"}]},
            {"level": 4, "proficiency_bonus": 2, "features": [{"name": "Ability Score Improvement"}]},
            {"level": 5, "proficiency_bonus": 3, "features": [{"name": "Uncanny Dodge"}, {"name": "Sneak Attack (3d6)"}]},
            {"level": 6, "proficiency_bonus": 3, "features": [{"name": "Expertise"}]},
            {"level": 7, "proficiency_bonus": 3, "features": [{"name": "Evasion"}, {"name": "Sneak Attack (4d6)"}]},
            {"level": 8, "proficiency_bonus": 3, "features": [{"name": "Ability Score Improvement"}]},
            {"level": 9, "proficiency_bonus": 4, "features": [{"name": "Roguish Archetype feature"}, {"name": "Sneak Attack (5d6)"}]},
            {"level": 10, "proficiency_bonus": 4, "features": [{"name": "Ability Score Improvement"}]},
            {"level": 11, "proficiency_bonus": 4, "features": [{"name": "Reliable Talent"}, {"name": "Sneak Attack (6d6)"}]},
            {"level": 12, "proficiency_bonus": 4, "features": [{"name": "Ability Score Improvement"}]},
            {"level": 13, "proficiency_bonus": 5, "features": [{"name": "Roguish Archetype feature"}, {"name": "Sneak Attack (7d6)"}]},
            {"level": 14, "proficiency_bonus": 5, "features": [{"name": "Blindsense"}]},
            {"level": 15, "proficiency_bonus": 5, "features": [{"name": "Slippery Mind"}, {"name": "Sneak Attack (8d6)"}]},
            {"level": 16, "proficiency_bonus": 5, "features": [{"name": "Ability Score Improvement"}]},
            {"level": 17, "proficiency_bonus": 6, "features": [{"name": "Roguish Archetype feature"}, {"name": "Sneak Attack (9d6)"}]},
            {"level": 18, "proficiency_bonus": 6, "features": [{"name": "Elusive"}]},
            {"level": 19, "proficiency_bonus": 6, "features": [{"name": "Ability Score Improvement"}, {"name": "Sneak Attack (10d6)"}]},
            {"level": 20, "proficiency_bonus": 6, "features": [{"name": "Stroke of Luck"}]},
        ]
    },
    {
        "class_data": {
            "name": "Sorcerer", 
            "description": "A spellcaster who draws on inherent magic from a gift or bloodline.", 
            "hit_die": 6
        },
        "levels": [
            {"level": 1, "proficiency_bonus": 2, "features": [{"name": "Spellcasting"}, {"name": "Sorcerous Origin"}], "spellcasting": {"cantrips_known": 4, "spells_known": 2, "spell_slots_level_1": 2, "spell_slots_level_2": 0, "spell_slots_level_3": 0, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 2, "proficiency_bonus": 2, "features": [{"name": "Font of Magic"}], "spellcasting": {"cantrips_known": 4, "spells_known": 3, "spell_slots_level_1": 3, "spell_slots_level_2": 0, "spell_slots_level_3": 0, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 3, "proficiency_bonus": 2, "features": [{"name": "Metamagic"}], "spellcasting": {"cantrips_known": 4, "spells_known": 4, "spell_slots_level_1": 4, "spell_slots_level_2": 2, "spell_slots_level_3": 0, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 4, "proficiency_bonus": 2, "features": [{"name": "Ability Score Improvement"}], "spellcasting": {"cantrips_known": 5, "spells_known": 5, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 0, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 5, "proficiency_bonus": 3, "features": [], "spellcasting": {"cantrips_known": 5, "spells_known": 6, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 2, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 6, "proficiency_bonus": 3, "features": [{"name": "Sorcerous Origin feature"}], "spellcasting": {"cantrips_known": 5, "spells_known": 7, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 0, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 7, "proficiency_bonus": 3, "features": [], "spellcasting": {"cantrips_known": 5, "spells_known": 8, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 1, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 8, "proficiency_bonus": 3, "features": [{"name": "Ability Score Improvement"}], "spellcasting": {"cantrips_known": 5, "spells_known": 9, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 2, "spell_slots_level_5": 0, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 9, "proficiency_bonus": 4, "features": [], "spellcasting": {"cantrips_known": 5, "spells_known": 10, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 1, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 10, "proficiency_bonus": 4, "features": [{"name": "Metamagic"}], "spellcasting": {"cantrips_known": 6, "spells_known": 11, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 0, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 11, "proficiency_bonus": 4, "features": [], "spellcasting": {"cantrips_known": 6, "spells_known": 12, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 12, "proficiency_bonus": 4, "features": [{"name": "Ability Score Improvement"}], "spellcasting": {"cantrips_known": 6, "spells_known": 12, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 0, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 13, "proficiency_bonus": 5, "features": [], "spellcasting": {"cantrips_known": 6, "spells_known": 13, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 14, "proficiency_bonus": 5, "features": [{"name": "Sorcerous Origin feature"}], "spellcasting": {"cantrips_known": 6, "spells_known": 13, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 0, "spell_slots_level_9": 0}},
            {"level": 15, "proficiency_bonus": 5, "features": [], "spellcasting": {"cantrips_known": 6, "spells_known": 14, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 1, "spell_slots_level_9": 0}},
            {"level": 16, "proficiency_bonus": 5, "features": [{"name": "Ability Score Improvement"}], "spellcasting": {"cantrips_known": 6, "spells_known": 14, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 1, "spell_slots_level_9": 0}},
            {"level": 17, "proficiency_bonus": 6, "features": [{"name": "Metamagic"}], "spellcasting": {"cantrips_known": 6, "spells_known": 15, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 2, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 1, "spell_slots_level_9": 1}},
            {"level": 18, "proficiency_bonus": 6, "features": [{"name": "Sorcerous Origin feature"}], "spellcasting": {"cantrips_known": 6, "spells_known": 15, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 3, "spell_slots_level_6": 1, "spell_slots_level_7": 1, "spell_slots_level_8": 1, "spell_slots_level_9": 1}},
            {"level": 19, "proficiency_bonus": 6, "features": [{"name": "Ability Score Improvement"}], "spellcasting": {"cantrips_known": 6, "spells_known": 15, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 3, "spell_slots_level_6": 2, "spell_slots_level_7": 1, "spell_slots_level_8": 1, "spell_slots_level_9": 1}},
            {"level": 20, "proficiency_bonus": 6, "features": [{"name": "Sorcerous Restoration"}], "spellcasting": {"cantrips_known": 6, "spells_known": 15, "spell_slots_level_1": 4, "spell_slots_level_2": 3, "spell_slots_level_3": 3, "spell_slots_level_4": 3, "spell_slots_level_5": 3, "spell_slots_level_6": 2, "spell_slots_level_7": 2, "spell_slots_level_8": 1, "spell_slots_level_9": 1}},
        ]
    }
    # You can add the full Cleric and Fighter data here as well.
]