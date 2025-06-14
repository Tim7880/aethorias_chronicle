# Path: api/app/models/background.py
from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.base_class import Base

class Background(Base):
    __tablename__ = "backgrounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Store list of skill names, e.g., ["Insight", "Religion"]
    skill_proficiencies = Column(JSON, nullable=False) 
    
    # Can be a number of choices or specific tools
    tool_proficiencies = Column(Text, nullable=True) 
    
    # Can be a number of choices or specific languages
    languages = Column(Text, nullable=True) 
    
    equipment = Column(Text, nullable=False)
    
    # The main unique feature of the background
    feature = Column(JSON, nullable=False) # e.g., {"name": "Shelter of the Faithful", "desc": "..."}
