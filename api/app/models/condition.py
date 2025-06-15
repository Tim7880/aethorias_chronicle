# Path: api/app/models/condition.py
from sqlalchemy import Column, Integer, String, Text
from app.db.base_class import Base

class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)

