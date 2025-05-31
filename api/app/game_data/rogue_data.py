# Path: api/app/game_data/rogue_data.py
from enum import Enum
from typing import List, Dict, Any

class RoguishArchetypeEnum(str, Enum):
    THIEF = "Thief"
    ASSASSIN = "Assassin"
    ARCANE_TRICKSTER = "Arcane Trickster"
    # Add other archetypes here if you expand beyond SRD

# Basic features granted at level 3 by each archetype (for future use/reference)
# For MVP, we might just store the archetype name.
# Detailed feature implementation is a larger step.
ROGUE_ARCHETYPE_FEATURES_L3: Dict[RoguishArchetypeEnum, List[Dict[str, Any]]] = {
    RoguishArchetypeEnum.THIEF: [
        {"name": "Fast Hands", "description": "Use the Cunning Action bonus action to make a Dexterity (Sleight of Hand) check, use thieves' tools to disarm a trap or open a lock, or take the Use an Object action."},
        {"name": "Second-Story Work", "description": "Climbing no longer costs you extra movement. When you make a running jump, the distance you cover increases by a number of feet equal to your Dexterity modifier."}
    ],
    RoguishArchetypeEnum.ASSASSIN: [
        {"name": "Assassinate", "description": "Advantage on attack rolls against any creature that hasn’t taken a turn in combat yet. Any hit you score against a creature that is surprised is a critical hit."},
        # Assassins also gain proficiency with the disguise kit and poisoner's kit.
        {"name": "Bonus Proficiencies (Assassin)", "description": "Proficiency with the disguise kit and the poisoner’s kit."} 
    ],
    RoguishArchetypeEnum.ARCANE_TRICKSTER: [
        {"name": "Spellcasting (Arcane Trickster)", "description": "You gain the ability to cast wizard spells. See PHB for spellcasting table, cantrips known, spells known."},
        {"name": "Mage Hand Legerdemain", "description": "Your Mage Hand cantrip gains additional capabilities."}
    ]
}

# List of available archetypes for validation/display
AVAILABLE_ROGUE_ARCHETYPES: List[RoguishArchetypeEnum] = [
    RoguishArchetypeEnum.THIEF,
    RoguishArchetypeEnum.ASSASSIN,
    RoguishArchetypeEnum.ARCANE_TRICKSTER
]