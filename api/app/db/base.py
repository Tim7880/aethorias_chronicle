# This file is used to ensure all SQLAlchemy models are imported before Base.metadata.create_all is called.
from app.db.base_class import Base  # Import the Base
from app.models.user import User  # Import your User model
from app.models.character import Character  # Import your Character model
from app.models.campaign import Campaign # Import your Campaign model
from app.models.campaign_member import CampaignMember # Import your CampaignMember model
from app.models.skill import Skill  # Import your Skill model
from app.models.character_skill import CharacterSkill # Import your CharacterSkill model




# Import other models here as you create them
# from app.models.character import Character
# from app.models.campaign import Campaign