from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.sql import expression # for server_default with Boolean
from app.db.base_class import Base # Import Base from our base_class.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    preferred_timezone = Column(String, nullable=True, server_default='UTC')
    is_active = Column(Boolean(), server_default=expression.true(), nullable=False)
    is_superuser = Column(Boolean(), server_default=expression.false(), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Add relationships later, e.g., to characters, campaigns
    # characters = relationship("Character", back_populates="owner")