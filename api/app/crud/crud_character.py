# Path: api/app/crud/crud_character.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func 
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple, Dict
import random

from app.models.character import Character as CharacterModel
from app.models.skill import Skill as SkillModel
from app.models.character_skill import CharacterSkill as CharacterSkillModel
from app.models.item import Item as ItemModel
from app.models.character_item import CharacterItem as CharacterItemModel
from app.models.spell import Spell as SpellModel
from app.models.character_spell import CharacterSpell as CharacterSpellModel
from app.models.dnd_class import DndClass as DndClassModel

from app.schemas.character import (
    CharacterCreate as CharacterCreateSchema,
    CharacterUpdate as CharacterUpdateSchema,
    ASISelectionRequest,
    SorcererSpellSelectionRequest as SpellSelectionRequest,
    ExpertiseSelectionRequest,
    RogueArchetypeSelectionRequest
)
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema, CharacterItemUpdate
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate 
from app.schemas.admin import AdminCharacterProgressionUpdate

from app.crud import crud_dnd_class, crud_item, crud_skill
from app.game_data.rogue_data import RoguishArchetypeEnum, AVAILABLE_ROGUE_ARCHETYPES

# --- Data Constants ---
XP_THRESHOLDS = { 
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
    9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
    15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
}
DEFAULT_STARTING_GP = 15
DEFAULT_STARTING_EQUIPMENT_PACK: List[Tuple[str, int]] = [ ("Backpack", 1), ("Bedroll", 1), ("Mess Kit", 1), ("Tinderbox", 1), ("Torch", 10), ("Rations (1 day)", 3), ("Waterskin", 1), ("Rope, Hempen (50 feet)", 1), ("Dagger", 1) ]
CLASS_SAVING_THROW_PROFICIENCIES: Dict[str, List[str]] = { "barbarian": ["strength", "constitution"], "bard": ["dexterity", "charisma"], "cleric": ["wisdom", "charisma"], "druid": ["intelligence", "wisdom"], "fighter": ["strength", "constitution"], "monk": ["strength", "dexterity"], "paladin": ["wisdom", "charisma"], "ranger": ["strength", "dexterity"], "rogue": ["dexterity", "intelligence"], "sorcerer": ["constitution", "charisma"], "warlock": ["wisdom", "charisma"], "wizard": ["intelligence", "wisdom"], }

# --- HELPER FUNCTIONS ---

def get_level_for_xp(xp: int) -> int:
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold: current_level = level
        else: break 
    return max(1, current_level)

def calculate_ability_modifier(score: Optional[int]) -> int:
    return (score - 10) // 2 if score is not None else 0

# --- GENERIC LEVEL-UP LOGIC ---

async def _character_gains_spells_at_level(character: CharacterModel, level_data: Dict, db: AsyncSession) -> bool:
    if not hasattr(level_data, 'spellcasting') or not level_data.spellcasting: return False
    
    spellcasting_info = level_data.spellcasting
    
    target_cantrips = spellcasting_info.get("cantrips_known", 0)
    if target_cantrips > 0:
        current_cantrips_q = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level == 0))
        if target_cantrips > current_cantrips_q.scalar_one(): return True

    if "spells_known" in spellcasting_info:
        target_spells_known = spellcasting_info.get("spells_known", 0)
        current_spells_q = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level > 0))
        if target_spells_known > current_spells_q.scalar_one(): return True
            
    return False

async def _get_next_level_up_status(character: CharacterModel, db: AsyncSession) -> Optional[str]:
    if not character.character_class: return None

    dnd_class = await crud_dnd_class.get_dnd_class_by_name(db, name=character.character_class)
    if not dnd_class or not dnd_class.levels: return None

    level_data = next((lvl for lvl in dnd_class.levels if lvl.level == character.level), None)
    if not level_data: return None

    completed_choices = character.completed_level_up_choices if isinstance(character.completed_level_up_choices, list) else []
    
    def choice_done(choice_type: str) -> bool:
        return any(c.get("level") == character.level and c.get("type") == choice_type for c in completed_choices)

    if not choice_done("hp") and character.level > 1 : return "pending_hp"

    if level_data.features:
        for feature in level_data.features:
            feature_name = feature.get("name", "").lower()
            if "ability score improvement" in feature_name and not choice_done("asi"): return "pending_asi"
            if "expertise" in feature_name and not choice_done("expertise"): return "pending_expertise"
            if "archetype" in feature_name and character.roguish_archetype is None: return "pending_archetype_selection"
    
    if hasattr(level_data, 'spellcasting') and level_data.spellcasting and not choice_done("spells"):
        if await _character_gains_spells_at_level(character, level_data, db):
            return "pending_spells"

    return None

# --- CHARACTER CORE CRUD ---

async def get_character(db: AsyncSession, character_id: int) -> Optional[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
        )
        .filter(CharacterModel.id == character_id)
    )
    return result.scalars().first()

async def get_characters_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[CharacterModel]:
    result = await db.execute(
        select(CharacterModel)
        .options(
            selectinload(CharacterModel.skills).selectinload(CharacterSkillModel.skill_definition),
            selectinload(CharacterModel.inventory_items).selectinload(CharacterItemModel.item_definition),
            selectinload(CharacterModel.known_spells).selectinload(CharacterSpellModel.spell_definition)
        )
        .filter(CharacterModel.user_id == user_id)
        .order_by(CharacterModel.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_character_for_user( db: AsyncSession, character_in: CharacterCreateSchema, user_id: int ) -> CharacterModel:
    character_data = character_in.model_dump(exclude={"chosen_cantrip_ids", "chosen_initial_spell_ids", "chosen_skill_proficiencies"})
    
    char_class_name = character_data.get("character_class")
    if not char_class_name: raise ValueError("A character class must be selected.")
        
    dnd_class = await crud_dnd_class.get_dnd_class_by_name(db, name=char_class_name)
    if not dnd_class: raise ValueError(f"Class '{char_class_name}' not found in database.")

    character_data["hit_die_type"] = dnd_class.hit_die
    character_data["level"] = 1
    character_data["experience_points"] = 0
    character_data["hit_dice_total"] = 1
    character_data["hit_dice_remaining"] = 1
    character_data["completed_level_up_choices"] = []
    character_data["level_up_status"] = None

    con_mod = calculate_ability_modifier(character_data.get("constitution", 10))
    character_data["hit_points_max"] = dnd_class.hit_die + con_mod
    character_data["hit_points_current"] = character_data["hit_points_max"]
    
    char_class_lower = char_class_name.lower()
    for prof in CLASS_SAVING_THROW_PROFICIENCIES.get(char_class_lower, []):
        field_name = f"st_prof_{prof}"
        character_data[field_name] = True

    db_character = CharacterModel(**character_data, user_id=user_id)
    db.add(db_character)
    
    await db.flush()

    for item_name, quantity in DEFAULT_STARTING_EQUIPMENT_PACK:
        item_model = await crud_item.get_item_by_name(db, name=item_name)
        if item_model:
            db.add(CharacterItemModel(character_id=db_character.id, item_id=item_model.id, quantity=quantity))

    if character_in.chosen_skill_proficiencies:
        for skill_id in set(character_in.chosen_skill_proficiencies):
            db.add(CharacterSkillModel(character_id=db_character.id, skill_id=skill_id, is_proficient=True))
    
    # Add initial spells if any were chosen
    if character_in.chosen_cantrip_ids:
        for spell_id in set(character_in.chosen_cantrip_ids):
            db.add(CharacterSpellModel(character_id=db_character.id, spell_id=spell_id, is_known=True, is_prepared=True))
    
    if character_in.chosen_initial_spell_ids:
        for spell_id in set(character_in.chosen_initial_spell_ids):
            db.add(CharacterSpellModel(character_id=db_character.id, spell_id=spell_id, is_known=True, is_prepared=True))

    db_character.level_up_status = await _get_next_level_up_status(db_character, db)
    
    await db.commit()
    await db.refresh(db_character)
    return await get_character(db, db_character.id)

async def update_character(db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field not in ["level", "experience_points", "hit_die_type", "hit_dice_total", "level_up_status", "completed_level_up_choices"]:
            setattr(character, field, value)
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def delete_character(db: AsyncSession, character_id: int, user_id: int) -> Optional[CharacterModel]:
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete); await db.commit()
        return character_to_delete
    return None


# --- All your other functions are preserved below ---

async def award_xp_to_character(db: AsyncSession, *, character: CharacterModel, xp_to_add: int) -> CharacterModel:
    if xp_to_add <= 0: raise ValueError("XP to award must be a positive integer.")
    current_xp = character.experience_points or 0
    character.experience_points = current_xp + xp_to_add
    new_level = get_level_for_xp(character.experience_points)
    if new_level > character.level:
        character.level = new_level
        character.hit_dice_total = new_level
        character.hit_dice_remaining = new_level
        character.completed_level_up_choices = [] 
        character.level_up_status = "pending_hp"
    db.add(character); await db.commit()
    return await get_character(db, character.id)

async def confirm_level_up_hp_increase(db: AsyncSession, *, character: CharacterModel, method: str = "average") -> Tuple[CharacterModel, int]:
    if character.level_up_status != "pending_hp":
        raise ValueError(f"Character is not pending HP confirmation. Status: {character.level_up_status}")
    dnd_class = await crud_dnd_class.get_dnd_class_by_name(db, name=character.character_class)
    if not dnd_class or not dnd_class.hit_die:
        raise ValueError(f"Character class data for '{character.character_class}' not found.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_gained_from_die = (dnd_class.hit_die // 2) + 1 if method == "average" else random.randint(1, dnd_class.hit_die)
    hp_gained_this_level = max(1, hp_gained_from_die + con_modifier)
    character.hit_points_max = (character.hit_points_max or 0) + hp_gained_this_level
    character.hit_points_current = character.hit_points_max
    if not isinstance(character.completed_level_up_choices, list): character.completed_level_up_choices = []
    character.completed_level_up_choices.append({"level": character.level, "type": "hp"})
    character.level_up_status = await _get_next_level_up_status(character, db)
    db.add(character); await db.commit()
    updated_character = await get_character(db, character.id)
    if not updated_character: raise Exception("Failed to reload character.")
    return updated_character, hp_gained_this_level

async def apply_character_asi(db: AsyncSession, *, character: CharacterModel, asi_selection: ASISelectionRequest) -> CharacterModel:
    if character.level_up_status != "pending_asi":
        raise ValueError(f"Character is not pending ASI selection.")
    for stat_name_str, increase_amount in asi_selection.stat_increases.items():
        stat_name_lower = stat_name_str.lower()
        current_score = getattr(character, stat_name_lower, 0)
        setattr(character, stat_name_lower, current_score + increase_amount)
    if not isinstance(character.completed_level_up_choices, list): character.completed_level_up_choices = []
    character.completed_level_up_choices.append({"level": character.level, "type": "asi"})
    character.level_up_status = await _get_next_level_up_status(character, db)
    db.add(character); await db.commit()
    return await get_character(db, character.id)

async def apply_spell_selections(db: AsyncSession, *, character: CharacterModel, spell_selection: SpellSelectionRequest) -> CharacterModel:
    if character.level_up_status != "pending_spells": 
        raise ValueError(f"Character is not pending spell selection.")
    for spell_id in spell_selection.chosen_cantrip_ids_on_level_up or []:
        await add_spell_to_character(db, character_id=character.id, spell_association_in=CharacterSpellCreate(spell_id=spell_id, is_known=True))
    for spell_id in spell_selection.new_leveled_spell_ids or []:
        await add_spell_to_character(db, character_id=character.id, spell_association_in=CharacterSpellCreate(spell_id=spell_id, is_known=True))
    if not isinstance(character.completed_level_up_choices, list): character.completed_level_up_choices = []
    character.completed_level_up_choices.append({"level": character.level, "type": "spells"})
    character.level_up_status = await _get_next_level_up_status(character, db)
    db.add(character); await db.commit()
    return await get_character(db, character.id)

async def apply_rogue_expertise(db: AsyncSession, *, character: CharacterModel, expertise_selection: ExpertiseSelectionRequest) -> CharacterModel:
    if character.level_up_status != "pending_expertise":
        raise ValueError("Character is not pending expertise selection.")
    for skill_id in expertise_selection.expert_skill_ids:
        char_skill_assoc = await get_character_skill_association(db, character_id=character.id, skill_id=skill_id)
        if not char_skill_assoc or not char_skill_assoc.is_proficient:
            raise ValueError(f"Cannot gain expertise in a skill you are not proficient with (ID: {skill_id}).")
        char_skill_assoc.has_expertise = True
        db.add(char_skill_assoc)
    if not isinstance(character.completed_level_up_choices, list): character.completed_level_up_choices = []
    character.completed_level_up_choices.append({"level": character.level, "type": "expertise"})
    character.level_up_status = await _get_next_level_up_status(character, db)
    db.add(character); await db.commit()
    return await get_character(db, character.id)

async def apply_rogue_archetype_selection(db: AsyncSession, *, character: CharacterModel, archetype_selection: RogueArchetypeSelectionRequest) -> CharacterModel:
    if character.level_up_status != "pending_archetype_selection":
        raise ValueError("Character is not pending archetype selection.")
    character.roguish_archetype = archetype_selection.archetype_name
    if not isinstance(character.completed_level_up_choices, list): character.completed_level_up_choices = []
    character.completed_level_up_choices.append({"level": character.level, "type": "archetype"})
    character.level_up_status = await _get_next_level_up_status(character, db)
    db.add(character); await db.commit()
    return await get_character(db, character.id)
    
# ... all other functions preserved ...
async def get_character_skill_association(db: AsyncSession, *, character_id: int, skill_id: int) -> Optional[CharacterSkillModel]:
    result = await db.execute(select(CharacterSkillModel).filter_by(character_id=character_id, skill_id=skill_id))
    return result.scalars().first()

async def assign_or_update_skill_proficiency_to_character(db: AsyncSession, *, character_id: int, skill_id: int, is_proficient: bool) -> CharacterSkillModel:
    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)
    if db_char_skill:
        db_char_skill.is_proficient = is_proficient
    else: 
        db_char_skill = CharacterSkillModel(character_id=character_id, skill_id=skill_id, is_proficient=is_proficient)
    db.add(db_char_skill)
    return db_char_skill

async def get_character_inventory_item(db: AsyncSession, *, character_id: int, item_id: int) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).filter_by(character_id=character_id, item_id=item_id))
    return result.scalars().first()

async def add_item_to_character_inventory(db: AsyncSession, *, character_id: int, item_in: CharacterItemCreateSchema) -> CharacterItemModel:
    db_character_item = await get_character_inventory_item(db=db, character_id=character_id, item_id=item_in.item_id)
    if db_character_item: db_character_item.quantity += item_in.quantity
    else: db_character_item = CharacterItemModel(character_id=character_id, **item_in.model_dump())
    db.add(db_character_item)
    return db_character_item

async def add_spell_to_character(db: AsyncSession, *, character_id: int, spell_association_in: CharacterSpellCreate) -> CharacterSpellModel:
    db_character_spell = CharacterSpellModel(character_id=character_id, **spell_association_in.model_dump())
    db.add(db_character_spell)
    return db_character_spell

async def update_character_inventory_item(db: AsyncSession, *, character_item_id: int, item_in: CharacterItemUpdate, character_id: int) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if not db_character_item: return None
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items(): setattr(db_character_item, field, value)
    if db_character_item.quantity <= 0: await db.delete(db_character_item); await db.commit(); return None 
    else: db.add(db_character_item); await db.commit(); await db.refresh(db_character_item); return db_character_item

async def remove_item_from_character_inventory(db: AsyncSession, *, character_id: int, character_item_id: int) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if db_character_item: await db.delete(db_character_item); await db.commit(); return db_character_item
    return None

async def get_character_spell_association(db: AsyncSession, *, character_id: int, spell_id: int) -> Optional[CharacterSpellModel]:
    result = await db.execute(select(CharacterSpellModel).filter_by(character_id=character_id, spell_id=spell_id))
    return result.scalars().first()

async def update_character_spell_association(db: AsyncSession, *, character_id: int, spell_id: int, spell_association_update_in: CharacterSpellUpdate) -> Optional[CharacterSpellModel]:
    db_char_spell = await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    if not db_char_spell: return None
    update_data = spell_association_update_in.model_dump(exclude_unset=True)
    if not update_data: return await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    for field, value in update_data.items(): setattr(db_char_spell, field, value)
    db.add(db_char_spell); await db.commit(); await db.refresh(db_char_spell)
    return await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    
async def remove_spell_from_character(db: AsyncSession, *, character_id: int, spell_id: int) -> Optional[CharacterSpellModel]:
    db_char_spell_to_delete = await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    if db_char_spell_to_delete: await db.delete(db_char_spell_to_delete); await db.commit(); return db_char_spell_to_delete
    return None
    
async def spend_character_hit_die(db: AsyncSession, *, character: CharacterModel, dice_roll_result: int) -> CharacterModel:
    if character.hit_dice_remaining is None or character.hit_dice_remaining <= 0: raise ValueError("No hit dice remaining to spend.")
    if not character.hit_die_type: raise ValueError("Character hit_die_type is not set.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_healed = max(1, dice_roll_result + con_modifier)
    character.hit_dice_remaining -= 1
    current_hp = character.hit_points_current or 0
    max_hp = character.hit_points_max or current_hp
    character.hit_points_current = min(current_hp + hp_healed, max_hp)
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def record_death_save(db: AsyncSession, *, character: CharacterModel, success: bool) -> CharacterModel:
    if success: character.death_save_successes = min((character.death_save_successes or 0) + 1, 3)
    else: character.death_save_failures = min((character.death_save_failures or 0) + 1, 3)
    if (character.death_save_successes or 0) >= 3 or (character.death_save_failures or 0) >= 3:
        character.death_save_successes = 0; character.death_save_failures = 0
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def reset_death_saves(db: AsyncSession, *, character: CharacterModel) -> CharacterModel:
    character.death_save_successes = 0; character.death_save_failures = 0
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def admin_update_character_progression(db: AsyncSession, *, character: CharacterModel, progression_in: AdminCharacterProgressionUpdate) -> CharacterModel:
    updated = False
    if progression_in.level is not None:
        max_level = 50 if character.is_ascended_tier else 20
        if not (1 <= progression_in.level <= max_level):
            raise ValueError(f"Admin: Target level ({progression_in.level}) is outside the allowed range (1-{max_level}).")
        character.level = progression_in.level
        character.experience_points = XP_THRESHOLDS.get(character.level, 0)
        
        dnd_class = await crud_dnd_class.get_dnd_class_by_name(db, name=character.character_class)
        if dnd_class and dnd_class.hit_die and character.constitution is not None:
            con_mod = calculate_ability_modifier(character.constitution)
            new_max_hp = dnd_class.hit_die + con_mod
            if character.level > 1:
                for _lvl in range(2, character.level + 1):
                    new_max_hp += max(1, (dnd_class.hit_die // 2) + 1 + con_mod)
            character.hit_points_max = new_max_hp
            character.hit_points_current = new_max_hp
        character.hit_dice_total = character.level
        character.hit_dice_remaining = character.level
        character.level_up_status = None 
        character.completed_level_up_choices = []
        updated = True
    
    if updated:
        db.add(character); await db.commit()
    return await get_character(db, character.id)
