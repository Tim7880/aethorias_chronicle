# Path: api/app/models/race.py
from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.base_class import Base

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # e.g., {"strength": 2, "constitution": 1}
    ability_score_increase = Column(JSON, nullable=False) 
    
    size = Column(String(50), nullable=False)
    speed = Column(Integer, nullable=False)
    
    # e.g., [{"name": "Dwarven Resilience", "desc": "..."}]
    racial_traits = Column(JSON) 
    
    languages = Column(Text) # e.g., "Common, Dwarvish"
    
    # --- MODIFICATION: Added subraces column ---
    # This will store a list of subrace objects, e.g., 
    # [{"name": "Hill Dwarf", "ability_score_increase": {"wisdom": 1}, "racial_traits": [{"name": "Dwarven Toughness", ...}]}]
    subraces = Column(JSON, nullable=True)
    # --- END MODIFICATION ---