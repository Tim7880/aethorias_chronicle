# Path: api/app/schemas/monster.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MonsterBase(BaseModel):
    name: str = Field(..., max_length=255)
    size: str = Field(..., max_length=50)
    creature_type: str = Field(..., max_length=100)
    alignment: str = Field(..., max_length=100)
    armor_class: int
    hit_points: int
    hit_dice: str = Field(..., max_length=50)
    speed: Dict[str, Any]
    
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    proficiencies: Optional[List[Dict[str, Any]]] = None
    damage_vulnerabilities: Optional[List[str]] = None
    damage_resistances: Optional[List[str]] = None
    damage_immunities: Optional[List[str]] = None
    condition_immunities: Optional[List[str]] = None
    senses: Dict[str, Any]
    languages: str
    challenge_rating: float
    xp: int

    special_abilities: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    legendary_actions: Optional[List[Dict[str, Any]]] = None

class MonsterCreate(MonsterBase):
    pass

class Monster(MonsterBase):
    id: int
    
    class Config:
        from_attributes = True

# --- NEW: Public-facing Monster Schema ---
# This schema omits sensitive DM-only information
class MonsterPublic(BaseModel):
    id: int
    name: str
    size: str
    creature_type: str
    alignment: str
    armor_class: int
    hit_dice: str # Show the dice, but not the calculated total HP
    speed: Dict[str, Any]
    
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    proficiencies: Optional[List[Dict[str, Any]]] = None
    damage_vulnerabilities: Optional[List[str]] = None
    damage_resistances: Optional[List[str]] = None
    damage_immunities: Optional[List[str]] = None
    condition_immunities: Optional[List[str]] = None
    senses: Dict[str, Any]
    languages: str

    special_abilities: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    legendary_actions: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
# --- END NEW ---


