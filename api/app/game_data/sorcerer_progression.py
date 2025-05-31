# Path: api/app/game_data/sorcerer_progression.py

# Sorcerer Cantrips Known and Spells Known per Level (D&D 5e PHB)
# Level: (Cantrips Known, Spells Known)
SORCERER_SPELLS_KNOWN_TABLE = {
    1:  (4, 2),  2:  (4, 3),  3:  (4, 4),  4:  (5, 5),  5:  (5, 6),
    6:  (5, 7),  7:  (5, 8),  8:  (5, 9),  9:  (5, 10), 10: (6, 11),
    11: (6, 12), 12: (6, 12), 13: (6, 13), 14: (6, 13), 15: (6, 14),
    16: (6, 14), 17: (6, 15), 18: (6, 15), 19: (6, 15), 20: (6, 15)
}

# Sorcerer Spell Slots per Spell Level (D&D 5e PHB)
# Level: {spell_level_1: slots, spell_level_2: slots, ..., spell_level_9: slots}
SORCERER_SPELL_SLOTS_TABLE = {
    1:  {1: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    2:  {1: 3, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    3:  {1: 4, 2: 2, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    4:  {1: 4, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    5:  {1: 4, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    6:  {1: 4, 2: 3, 3: 3, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    7:  {1: 4, 2: 3, 3: 3, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    8:  {1: 4, 2: 3, 3: 3, 4: 2, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
    9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0}, # Also gain Metamagic
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0}, # 6th level slot
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0, 8: 0, 9: 0},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0}, # 7th level slot
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0, 9: 0},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0}, # 8th level slot
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 0},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1}, # 9th level slot, Sorcerous Restoration
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}  # Also gain Sorcerous Restoration
}

# Helper to determine max spell level a sorcerer can know/cast based on available slots
def get_sorcerer_max_spell_level_can_learn(sorcerer_level: int) -> int:
    if not (1 <= sorcerer_level <= 20):
        return 0 # Or raise error

    slots = SORCERER_SPELL_SLOTS_TABLE.get(sorcerer_level, {})
    for spell_level in range(9, 0, -1): # Check from 9th level down to 1st
        if slots.get(spell_level, 0) > 0:
            return spell_level
    return 0 # Should not happen for L1+ sorcerers, they always have L1 slots