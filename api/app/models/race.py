# Path: api/app/models/race.py
from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.base_class import Base

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Store complex, variable data as JSON. This is very flexible.
    # e.g., {"strength": 2, "constitution": 1}
    ability_score_increase = Column(JSON, nullable=False) 
    
    size = Column(String(50), nullable=False)
    speed = Column(Integer, nullable=False)
    
    # e.g., ["Darkvision", {"name": "Dwarven Resilience", "desc": "You have advantage on saving throws against poison..."}]
    racial_traits = Column(JSON) 
    
    languages = Column(Text) # e.g., "Common, Dwarvish"
    
    # You could add a subraces field here later if needed, e.g. as a JSON field or a separate table
    # subraces = Column(JSON) 