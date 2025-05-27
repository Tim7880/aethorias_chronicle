# Path: api/app/db/base.py
# This file is used to ensure all SQLAlchemy models are imported before Base.metadata.create_all is called.
from app.db.base_class import Base  # Import the Base

from app.models.user import User
from app.models.character import Character
from app.models.campaign import Campaign
from app.models.campaign_member import CampaignMember
from app.models.skill import Skill
from app.models.character_skill import CharacterSkill
from app.models.item import Item
from app.models.character_item import CharacterItem
from app.models.spell import Spell
from app.models.character_spell import CharacterSpell # <--- ADD THIS IMPORT

# Import other models here as you create them
# Import other models here as you create them




# Import other models here as you create them
# from app.models.character import Character
# from app.models.campaign import Campaign