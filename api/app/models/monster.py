# Path: api/app/models/monster.py
from sqlalchemy import Column, Integer, String, Float, JSON, Text
from app.db.base_class import Base

class Monster(Base):
    __tablename__ = "monsters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    size = Column(String(50), nullable=False)
    creature_type = Column(String(100), nullable=False)
    alignment = Column(String(100), nullable=False)
    
    armor_class = Column(Integer, nullable=False)
    hit_points = Column(Integer, nullable=False)
    hit_dice = Column(String(50), nullable=False)
    speed = Column(JSON, nullable=False)

    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)

    proficiencies = Column(JSON) # e.g., [{"proficiency": {"name": "Stealth"}, "value": 6}]
    damage_vulnerabilities = Column(JSON) # e.g., ["Fire", "Radiant"]
    damage_resistances = Column(JSON)
    damage_immunities = Column(JSON)
    condition_immunities = Column(JSON)
    
    senses = Column(JSON, nullable=False) # e.g., {"darkvision": "60 ft.", "passive_perception": 10}
    languages = Column(Text)
    challenge_rating = Column(Float, nullable=False)
    xp = Column(Integer, nullable=False)

    special_abilities = Column(JSON)
    actions = Column(JSON)
    legendary_actions = Column(JSON)
