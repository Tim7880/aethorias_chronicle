# This file is used to ensure all SQLAlchemy models are imported before Base.metadata.create_all is called.
from app.db.base_class import Base  # Import the Base
from app.models.user import User  # Import your User model
# Import other models here as you create them
# from app.models.character import Character
# from app.models.campaign import Campaign