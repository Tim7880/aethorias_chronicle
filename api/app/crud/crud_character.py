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

from app.schemas.character import (
    CharacterCreate as CharacterCreateSchema,
    CharacterUpdate as CharacterUpdateSchema,
    ASISelectionRequest,
    SorcererSpellSelectionRequest,
    ExpertiseSelectionRequest,
    RogueArchetypeSelectionRequest # Ensure this is imported
)
from app.schemas.skill import CharacterSkillCreate as CharacterSkillCreateSchema
from app.schemas.item import CharacterItemCreate as CharacterItemCreateSchema
from app.schemas.item import CharacterItemUpdate as CharacterItemUpdateSchema
from app.schemas.character_spell import CharacterSpellCreate, CharacterSpellUpdate 
from app.schemas.admin import AdminCharacterProgressionUpdate

# --- Game Data Imports ---
from app.game_data.sorcerer_progression import (
    SORCERER_SPELLS_KNOWN_TABLE,
    get_sorcerer_max_spell_level_can_learn
)
from app.game_data.rogue_data import RoguishArchetypeEnum, AVAILABLE_ROGUE_ARCHETYPES # For Rogue Archetype
from app.schemas.character import RogueArchetypeSelectionRequest
# --- XP, Leveling, ASI, Hit Dice, Expertise, Archetype Definitions ---
XP_THRESHOLDS = { 
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
    9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
    15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
    21: 410000, 22: 470000, 23: 535000, 24: 605000, 25: 680000,
    26: 760000, 27: 845000, 28: 935000, 29: 1030000, 30: 1130000,
    31: 1240000, 32: 1360000, 33: 1490000, 34: 1630000, 35: 1780000,
    36: 1940000, 37: 2110000, 38: 2290000, 39: 2480000, 40: 2680000,
    41: 2900000, 42: 3140000, 43: 3400000, 44: 3680000, 45: 3980000,
    46: 4300000, 47: 4640000, 48: 5000000, 49: 5380000, 50: 5780000
}

CLASS_HIT_DIE_MAP = {
    "artificer": 8, "barbarian": 12, "bard": 8, "cleric": 8, "druid": 8,
    "fighter": 10, "monk": 8, "paladin": 10, "ranger": 10, "rogue": 8,
    "sorcerer": 6, "warlock": 8, "wizard": 6
}

CLASS_ASI_LEVELS_MAP: Dict[str, List[int]] = {
    "fighter": [4, 6, 8, 12, 14, 16, 19],
    "rogue": [4, 8, 10, 12, 16, 19],
    "default": [4, 8, 12, 16, 19] 
}

ROGUE_EXPERTISE_LEVELS = [1, 6]
ROGUE_ARCHETYPE_LEVEL = 3

async def _get_next_level_up_status(character: CharacterModel, db: AsyncSession) -> Optional[str]:
    """Helper function to determine the next pending level-up status."""
    char_class_lower = character.character_class.lower() if character.character_class else None
    current_level = character.level

    # Order of priority for level-up choices:
    # 1. Rogue Archetype (at L3, if not yet chosen and character is L3+)
    if is_rogue_archetype_due(char_class_lower, current_level) and not character.roguish_archetype:
        return "pending_archetype_selection"
    
    # 2. ASI (Ability Score Increase)
    if is_asi_due(char_class_lower, current_level):
        # TODO: Future - Need a way to track if ASI for *this specific level* was already taken.
        # For now, if an ASI level is reached and previous steps are done, flag it.
        return "pending_asi"
        
    # 3. Rogue Expertise (L1 handled at creation, this is for L6)
    if is_rogue_expertise_due(char_class_lower, current_level):
        # L1 expertise is set during character creation's level_up_status.
        # This handles L6 expertise.
        # TODO: Future - Need to check if L6 expertise was already chosen for this level.
        # Count existing expertises; Rogues get 2 at L1 and 2 more at L6. Total 4 by L6.
        expert_skills_count = 0
        if character.skills: # Ensure character.skills is loaded if accessed this way
            # This requires character.skills to be loaded, get_character() does this.
            # If character passed in doesn't have skills loaded, this will be 0 or error.
            # Assuming character object passed in has relationships loaded from get_character()
            expert_skills_count = sum(1 for sk_assoc in character.skills if sk_assoc.has_expertise)

        if current_level == 1 and expert_skills_count < 2:
            return "pending_expertise" # Should have been set by create_character
        if current_level == 6 and expert_skills_count < 4:
            return "pending_expertise"

    # 4. Sorcerer Spell Selection
    if char_class_lower == "sorcerer" and \
       await _sorcerer_gains_cantrip_or_spell_at_level(current_level, db=db, character_id=character.id):
        return "pending_spells"

    # TODO: Add checks for other class-specific feature choices here
    
    return None # All choices for this level up are complete

def get_level_for_xp(xp: int, is_ascended_tier: bool = False) -> int:
    current_level = 0
    for level, threshold in XP_THRESHOLDS.items():
        if xp >= threshold: current_level = level
        else: break 
    return max(1, current_level)

def get_xp_for_level(level: int) -> int:
    return XP_THRESHOLDS.get(level, 0)

def calculate_ability_modifier(score: Optional[int]) -> int:
    if score is None: return 0
    return (score - 10) // 2

def is_asi_due(character_class_name: Optional[str], new_level: int) -> bool:
    if not character_class_name: return False 
    class_key = character_class_name.lower()
    asi_levels = CLASS_ASI_LEVELS_MAP.get(class_key, CLASS_ASI_LEVELS_MAP.get("default", []))
    return new_level in asi_levels

def is_rogue_expertise_due(character_class_name: Optional[str], level: int) -> bool:
    if not character_class_name or character_class_name.lower() != "rogue":
        return False
    return level in ROGUE_EXPERTISE_LEVELS

def is_rogue_archetype_due(character_class_name: Optional[str], level: int) -> bool:
    if not character_class_name or character_class_name.lower() != "rogue":
        return False
    return level >= ROGUE_ARCHETYPE_LEVEL # Due if level is 3 or more and no archetype selected yet

async def _sorcerer_gains_cantrip_or_spell_at_level(level: int, db: AsyncSession, character_id: int) -> bool:
    if not character_id: return False # Should not happen if character object exists
    if not (1 < level <= 20): return False 
    target_cantrips, target_spells_known = SORCERER_SPELLS_KNOWN_TABLE.get(level, (0,0))
    current_cantrips_q = await db.execute(
        select(func.count(CharacterSpellModel.id))
        .join(SpellModel, CharacterSpellModel.spell_id == SpellModel.id)
        .filter(CharacterSpellModel.character_id == character_id, CharacterSpellModel.is_known == True, SpellModel.level == 0)
    )
    current_cantrips_count = current_cantrips_q.scalar_one_or_none() or 0
    current_spells_q = await db.execute(
        select(func.count(CharacterSpellModel.id))
        .join(SpellModel, CharacterSpellModel.spell_id == SpellModel.id)
        .filter(CharacterSpellModel.character_id == character_id, CharacterSpellModel.is_known == True, SpellModel.level > 0)
    )
    current_spells_count = current_spells_q.scalar_one_or_none() or 0
    gains_cantrip = target_cantrips > current_cantrips_count
    gains_spell = target_spells_known > current_spells_count
    can_swap_spell = True 
    return gains_cantrip or gains_spell or can_swap_spell

# --- Character Core CRUD ---
async def create_character_for_user(
    db: AsyncSession, character_in: CharacterCreateSchema, user_id: int
) -> CharacterModel:
    character_data = character_in.model_dump(exclude={"chosen_cantrip_ids", "chosen_initial_spell_ids"}) 
    
    char_class_lower = None
    if character_data.get("character_class"):
        char_class_lower = character_data["character_class"].lower()
    
    hit_die_type_value = CLASS_HIT_DIE_MAP.get(char_class_lower)
    character_data["hit_die_type"] = hit_die_type_value
    
    if character_data.get("experience_points") is not None:
        character_data["level"] = get_level_for_xp(character_data["experience_points"], character_data.get("is_ascended_tier", False))
    elif character_data.get("level") is None:
         character_data["level"] = 1
    
    initial_level = character_data["level"]
    character_data["hit_dice_total"] = initial_level
    character_data["hit_dice_remaining"] = initial_level
    character_data["death_save_successes"] = character_data.get("death_save_successes", 0)
    character_data["death_save_failures"] = character_data.get("death_save_failures", 0)
    
    # Set initial level_up_status based on L1 features
    # Set initial level_up_status based on L1 features
    if initial_level == 1 and is_rogue_expertise_due(char_class_lower, initial_level) and \
       not character_data.get("roguish_archetype"): # Rogues choose L1 expertise
        character_data["level_up_status"] = "pending_expertise"
    # Add other L1 specific choices here if any (e.g. Fighter fighting style)
    # elif initial_level == 1 and is_fighter_fighting_style_due(char_class_lower, initial_level):
    #     character_data["level_up_status"] = "pending_fighting_style"
    else:
        character_data["level_up_status"] = None # Default if no immediate L1 choices
    # --- END MODIFICATION ---
    # Initial HP calculation
    if character_data.get("hit_points_max") is None: # Only calculate if not provided
        if hit_die_type_value and character_data.get("constitution") is not None:
            con_modifier = calculate_ability_modifier(character_data["constitution"])
            calculated_hp = 0
            if initial_level == 1:
                calculated_hp = hit_die_type_value + con_modifier
            elif initial_level > 1: 
                calculated_hp = hit_die_type_value + con_modifier 
                for _ in range(2, initial_level + 1): 
                    calculated_hp += max(1, (hit_die_type_value // 2) + 1 + con_modifier)
            character_data["hit_points_max"] = calculated_hp
    
    if character_data.get("hit_points_max") is not None and character_data.get("hit_points_current") is None:
        character_data["hit_points_current"] = character_data["hit_points_max"]
            
    db_character = CharacterModel(**character_data, user_id=user_id)
    db.add(db_character)
    
    try:
        await db.commit()
        await db.refresh(db_character)
    except Exception as e: 
        await db.rollback()
        raise ValueError(f"Error creating character base record: {e}")

    # Process initial cantrips and spells (Sorcerer L1 example)
    if char_class_lower == "sorcerer" and db_character.level == 1:
        expected_cantrips, expected_spells_lvl1 = SORCERER_SPELLS_KNOWN_TABLE.get(1, (0,0))
        if character_in.chosen_cantrip_ids:
            if len(set(character_in.chosen_cantrip_ids)) != expected_cantrips:
                # Consider deleting the already committed character if this part fails, for true atomicity
                # For now, raising ValueError. The character exists but without these spells.
                raise ValueError(f"Sorcerers at L1 must choose {expected_cantrips} unique cantrips.")
            for spell_id in set(character_in.chosen_cantrip_ids):
                spell_def = await db.get(SpellModel, spell_id)
                if not spell_def or spell_def.level != 0: raise ValueError(f"Invalid cantrip ID {spell_id}.")
                if not (spell_def.dnd_classes and "sorcerer" in [c.lower() for c in spell_def.dnd_classes]): raise ValueError(f"Spell ID {spell_id} not a Sorcerer cantrip.")
                db.add(CharacterSpellModel(character_id=db_character.id, spell_id=spell_id, is_known=True, is_prepared=True))
        elif expected_cantrips > 0: raise ValueError(f"Sorcerers at L1 must select {expected_cantrips} cantrips.")
        
        if character_in.chosen_initial_spell_ids:
            if len(set(character_in.chosen_initial_spell_ids)) != expected_spells_lvl1:
                raise ValueError(f"Sorcerers at L1 must choose {expected_spells_lvl1} unique L1 spells.")
            for spell_id in set(character_in.chosen_initial_spell_ids):
                spell_def = await db.get(SpellModel, spell_id)
                if not spell_def or spell_def.level != 1: raise ValueError(f"Invalid L1 spell ID {spell_id}.")
                if not (spell_def.dnd_classes and "sorcerer" in [c.lower() for c in spell_def.dnd_classes]): raise ValueError(f"Spell ID {spell_id} not a Sorcerer spell.")
                if spell_id in (character_in.chosen_cantrip_ids or []): raise ValueError(f"Spell ID {spell_id} chosen as cantrip and L1 spell.")
                db.add(CharacterSpellModel(character_id=db_character.id, spell_id=spell_id, is_known=True, is_prepared=True))
        elif expected_spells_lvl1 > 0: raise ValueError(f"Sorcerers at L1 must select {expected_spells_lvl1} L1 spells.")
            
        if character_in.chosen_cantrip_ids or character_in.chosen_initial_spell_ids:
            try: await db.commit() # Commit spell associations
            except Exception as e: await db.rollback(); raise ValueError(f"Error adding initial spells: {e}")
    
    return await get_character(db, db_character.id) # Ensures all relationships are loaded


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

async def get_characters_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[CharacterModel]:
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

async def update_character(
    db: AsyncSession, character: CharacterModel, character_in: CharacterUpdateSchema
) -> CharacterModel:
    update_data = character_in.model_dump(exclude_unset=True)
    if "character_class" in update_data and update_data["character_class"] is not None:
        new_class_name_lower = update_data["character_class"].lower()
        character.hit_die_type = CLASS_HIT_DIE_MAP.get(new_class_name_lower)
    for field, value in update_data.items():
        if field == "character_class" and "hit_die_type" in update_data: 
            setattr(character, field, value)
        elif field not in ["level", "experience_points", "hit_die_type", "hit_dice_total", "level_up_status"]:
            setattr(character, field, value)
    if character.hit_points_current is not None and character.hit_points_max is not None:
        if character.hit_points_current > character.hit_points_max:
            character.hit_points_current = character.hit_points_max
    if character.hit_dice_remaining is not None and character.hit_dice_total is not None:
         if character.hit_dice_remaining > character.hit_dice_total:
            character.hit_dice_remaining = character.hit_dice_total
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def delete_character(
    db: AsyncSession, character_id: int, user_id: int 
) -> Optional[CharacterModel]:
    character_to_delete = await get_character(db=db, character_id=character_id) 
    if character_to_delete and character_to_delete.user_id == user_id:
        await db.delete(character_to_delete)
        await db.commit()
        return character_to_delete
    return None

async def award_xp_to_character(
    db: AsyncSession, *, character: CharacterModel, xp_to_add: int
) -> CharacterModel:
    if xp_to_add <= 0: raise ValueError("XP to award must be a positive integer.")
    current_xp = character.experience_points if character.experience_points is not None else 0
    character.experience_points = current_xp + xp_to_add
    new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
    
    if new_level > character.level:
        print(f"Character {character.name} (ID: {character.id}) is eligible for level {new_level} (was {character.level})!")
        character.level = new_level 
        character.hit_dice_total = new_level 
        character.hit_dice_remaining = new_level # Regain all hit dice on level up
        
        # --- START MODIFICATION: Set initial status for the new level choices ---
        # Always start with HP confirmation unless it's an L1 Rogue (handled by creation)
        # or another L1 immediate choice.
        char_class_lower = character.character_class.lower() if character.character_class else None
        if new_level == 1 and is_rogue_expertise_due(char_class_lower, new_level): # Should be covered by create_character
            character.level_up_status = "pending_expertise"
        else:
            character.level_up_status = "pending_hp" # HP is always the first step after level number changes
        # --- END MODIFICATION ---
        
        print(f"Character {character.name} is now level {character.level}. Status: {character.level_up_status}")
    else:
        if character.level_up_status is not None: 
            character.level_up_status = None 
            print(f"Character {character.name} XP updated. No level change. Level up status cleared.")
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def confirm_level_up_hp_increase(
    db: AsyncSession, *, character: CharacterModel, method: str = "average"
) -> Tuple[CharacterModel, int]:
    if character.level_up_status != "pending_hp": raise ValueError(f"Character is not pending HP confirmation. Current status: {character.level_up_status}")
    if not character.hit_die_type: raise ValueError("Character hit_die_type is not set. Cannot calculate HP.")
    
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_gained_from_die = (character.hit_die_type // 2) + 1 if method == "average" else random.randint(1, character.hit_die_type)
    if method not in ["average", "roll"]: raise ValueError("Invalid HP increase method. Choose 'average' or 'roll'.")
    hp_gained_this_level = max(1, hp_gained_from_die + con_modifier)
    
    current_max_hp = character.hit_points_max if character.hit_points_max is not None else 0
    if character.level == 1 and current_max_hp == 0: 
        character.hit_points_max = character.hit_die_type + con_modifier
    elif character.level > 1 : 
        character.hit_points_max = current_max_hp + hp_gained_this_level
        
    character.hit_points_current = character.hit_points_max
    character.level_up_status = await _get_next_level_up_status(character, db)
    char_class_lower = character.character_class.lower() if character.character_class else None
    if is_rogue_archetype_due(char_class_lower, character.level) and not character.roguish_archetype:
        character.level_up_status = "pending_archetype_selection"
    elif is_asi_due(character.character_class, character.level): 
        character.level_up_status = "pending_asi"
    elif char_class_lower == "sorcerer" and \
         await _sorcerer_gains_cantrip_or_spell_at_level(character.level, db=db, character_id=character.id):
        character.level_up_status = "pending_spells"
    elif is_rogue_expertise_due(char_class_lower, character.level) and character.level > 1 :
        character.level_up_status = "pending_expertise"
    else: 
        character.level_up_status = None 
    
    print(f"Character {character.name} HP increased by {hp_gained_this_level}. New Max HP: {character.hit_points_max}. Status set to: {character.level_up_status}")
    db.add(character); await db.commit(); await db.refresh(character)
    updated_character = await get_character(db, character.id)
    if not updated_character: raise Exception("Failed to reload character after HP increase.")
    return updated_character, hp_gained_this_level

async def apply_character_asi(
    db: AsyncSession, *, character: CharacterModel, asi_selection: ASISelectionRequest
) -> CharacterModel:
    if character.level_up_status != "pending_asi": raise ValueError(f"Character is not pending ASI selection. Current status: {character.level_up_status}")
    
    max_stat_for_tier = 50 if character.is_ascended_tier else 30 
    for stat_name_str, increase_amount in asi_selection.stat_increases.items():
        stat_name_lower = stat_name_str.lower()
        current_score = getattr(character, stat_name_lower, None)
        if current_score is None: raise ValueError(f"Invalid stat name '{stat_name_str}' for ASI.")
        new_score = current_score + increase_amount
        if new_score > max_stat_for_tier: raise ValueError(f"ASI for {stat_name_str} to {new_score} would exceed tier maximum of {max_stat_for_tier}.")
        setattr(character, stat_name_lower, new_score)
        print(f"Character {character.name} {stat_name_str} increased by {increase_amount} to {new_score}.")
    
    character.level_up_status = await _get_next_level_up_status(character, db)
    char_class_lower = character.character_class.lower() if character.character_class else None
    if char_class_lower == "sorcerer" and \
         await _sorcerer_gains_cantrip_or_spell_at_level(character.level, db=db, character_id=character.id):
        character.level_up_status = "pending_spells"
    elif is_rogue_expertise_due(char_class_lower, character.level) and character.level > 1 : # L6 Expertise for Rogue
        character.level_up_status = "pending_expertise"
    else:
        character.level_up_status = None
    print(f"Character {character.name} ASI applied. Level up status set to: {character.level_up_status}")
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

async def apply_rogue_expertise(
    db: AsyncSession,
    *,
    character: CharacterModel,
    expertise_selection: ExpertiseSelectionRequest
) -> CharacterModel:
    if not character.character_class or character.character_class.lower() != "rogue":
        raise ValueError("Expertise selection is for Rogue class characters only.")
    if character.level_up_status != "pending_expertise":
        raise ValueError(f"Character is not pending expertise selection. Current status: {character.level_up_status}")
    if not is_rogue_expertise_due(character.character_class, character.level):
        raise ValueError(f"Character (Rogue L{character.level}) is not due for expertise selection at this level.")

    if len(expertise_selection.expert_skill_ids) != 2:
        raise ValueError("Rogue must select exactly two skill proficiencies for expertise.")

    updated_skills_count = 0
    for skill_id in expertise_selection.expert_skill_ids:
        char_skill_assoc = await get_character_skill_association(db, character_id=character.id, skill_id=skill_id)
        if not char_skill_assoc or not char_skill_assoc.is_proficient:
            skill_info_res = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
            skill_info = skill_info_res.scalars().first()
            skill_name = skill_info.name if skill_info else f"ID {skill_id}"
            raise ValueError(f"Character must be proficient in skill '{skill_name}' (ID: {skill_id}) to select it for expertise.")
        if char_skill_assoc.has_expertise:
            skill_info_res = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
            skill_info = skill_info_res.scalars().first()
            skill_name = skill_info.name if skill_info else f"ID {skill_id}"
            raise ValueError(f"Character already has expertise in '{skill_name}' (ID: {skill_id}).")
        
        char_skill_assoc.has_expertise = True
        db.add(char_skill_assoc)
        updated_skills_count +=1
        skill_info_res = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
        skill_info = skill_info_res.scalars().first()
        print(f"Character {character.name} gained expertise in skill '{skill_info.name if skill_info else skill_id}'.")

    if updated_skills_count != len(expertise_selection.expert_skill_ids): # Should be 2
        await db.rollback() 
        raise ValueError("Failed to update expertise for all selected skills. Ensure choices are valid.")
    
    character.level_up_status = await _get_next_level_up_status(character, db)

    # After expertise, determine next state (e.g., L1 Rogue is done with L1 choices)
    # L6 Rogue might have other L6 features or just be done with this expertise choice.
    # For now, assume this completes the 'pending_expertise' state.
    character.level_up_status = None 
    print(f"Character {character.name} Rogue expertise selection complete. Level up status: {character.level_up_status}")
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def apply_rogue_archetype_selection(
    db: AsyncSession,
    *,
    character: CharacterModel,
    archetype_selection: RogueArchetypeSelectionRequest
) -> CharacterModel:
    if not character.character_class or character.character_class.lower() != "rogue":
        raise ValueError("Archetype selection is for Rogue class characters only.")
    # Check if archetype is due at this level and if one hasn't been selected
    if not is_rogue_archetype_due(character.character_class, character.level) or character.roguish_archetype is not None:
        if character.roguish_archetype is not None:
             raise ValueError(f"Character has already selected the archetype: {character.roguish_archetype.value}")
        else:
             raise ValueError(f"Rogue archetype selection is not due at level {character.level}.")

    if character.level_up_status != "pending_archetype_selection":
        raise ValueError(f"Character is not pending archetype selection. Current status: {character.level_up_status}")

    chosen_archetype_enum: RoguishArchetypeEnum = archetype_selection.archetype_name
    if chosen_archetype_enum not in AVAILABLE_ROGUE_ARCHETYPES:
        raise ValueError(f"Invalid archetype '{chosen_archetype_enum.value}' selected for Rogue.")

    character.roguish_archetype = chosen_archetype_enum
    print(f"Character {character.name} selected archetype: {chosen_archetype_enum.value}.")

    # TODO: Grant specific L3 features based on archetype here.
    # For example, if chosen_archetype == RoguishArchetypeEnum.ASSASSIN:
    #   await grant_proficiency(db, character, "disguise_kit_tool_id") # Needs tool proficiency system
    #   await grant_proficiency(db, character, "poisoners_kit_tool_id")
    # This requires a system for tracking tool proficiencies and a way to add them.
    # For Arcane Trickster, it would involve adding spells to their known_spells.
    # This class-specific feature granting will be a future step.

    # Determine next status after Archetype selection
    character.level_up_status = await _get_next_level_up_status(character, db)
    
    print(f"Character {character.name} Rogue archetype selection complete. Level up status: {character.level_up_status}")
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)


# --- Character Skill Management Functions ---
async def get_character_skill_association(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    result = await db.execute(select(CharacterSkillModel).filter_by(character_id=character_id, skill_id=skill_id))
    return result.scalars().first()

async def assign_or_update_skill_proficiency_to_character(
    db: AsyncSession, *, character_id: int, skill_id: int, is_proficient: bool
) -> CharacterSkillModel:
    skill_result = await db.execute(select(SkillModel).filter(SkillModel.id == skill_id))
    if not skill_result.scalars().first(): raise ValueError(f"Skill with id {skill_id} not found.") 
    db_char_skill = await get_character_skill_association(db=db, character_id=character_id, skill_id=skill_id)
    if db_char_skill:
        if db_char_skill.is_proficient != is_proficient:
            db_char_skill.is_proficient = is_proficient; db.add(db_char_skill)
    else: 
        db_char_skill = CharacterSkillModel(character_id=character_id, skill_id=skill_id, is_proficient=is_proficient, has_expertise=False)
        db.add(db_char_skill)
    await db.commit(); await db.refresh(db_char_skill)
    result_with_skill_def = await db.execute(select(CharacterSkillModel).options(selectinload(CharacterSkillModel.skill_definition)).filter(CharacterSkillModel.id == db_char_skill.id))
    return result_with_skill_def.scalars().first()

async def remove_skill_from_character(
    db: AsyncSession, *, character_id: int, skill_id: int
) -> Optional[CharacterSkillModel]:
    db_char_skill_to_delete = await db.execute(select(CharacterSkillModel).options(selectinload(CharacterSkillModel.skill_definition)).filter_by(character_id=character_id, skill_id=skill_id))
    db_char_skill = db_char_skill_to_delete.scalars().first()
    if db_char_skill: await db.delete(db_char_skill); await db.commit(); return db_char_skill
    return None

# --- Character Inventory Item Management Functions ---
async def get_character_inventory_item(
    db: AsyncSession, *, character_id: int, item_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).filter_by(character_id=character_id, item_id=item_id))
    return result.scalars().first()

async def add_item_to_character_inventory(
    db: AsyncSession, *, character_id: int, item_in: CharacterItemCreateSchema
) -> CharacterItemModel:
    item_definition_res = await db.execute(select(ItemModel).filter(ItemModel.id == item_in.item_id))
    if not item_definition_res.scalars().first(): raise ValueError(f"Item with ID {item_in.item_id} not found.")
    db_character_item = await get_character_inventory_item(db=db, character_id=character_id, item_id=item_in.item_id)
    if db_character_item: db_character_item.quantity += item_in.quantity
    else: db_character_item = CharacterItemModel(character_id=character_id, item_id=item_in.item_id, quantity=item_in.quantity, is_equipped=item_in.is_equipped)
    db.add(db_character_item); await db.commit(); await db.refresh(db_character_item)
    result_with_item_def = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == db_character_item.id))
    return result_with_item_def.scalars().first()

async def update_character_inventory_item(
    db: AsyncSession, *, character_item_id: int, item_in: CharacterItemUpdateSchema, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if not db_character_item: return None
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items(): setattr(db_character_item, field, value)
    if db_character_item.quantity <= 0: await db.delete(db_character_item); await db.commit(); return None 
    else: db.add(db_character_item); await db.commit(); await db.refresh(db_character_item); return db_character_item

async def remove_item_from_character_inventory(
    db: AsyncSession, *, character_item_id: int, character_id: int
) -> Optional[CharacterItemModel]:
    result = await db.execute(select(CharacterItemModel).options(selectinload(CharacterItemModel.item_definition)).filter(CharacterItemModel.id == character_item_id, CharacterItemModel.character_id == character_id))
    db_character_item = result.scalars().first()
    if db_character_item: await db.delete(db_character_item); await db.commit(); return db_character_item
    return None

# --- Character Spell Management Functions ---
async def get_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    result = await db.execute(select(CharacterSpellModel).filter_by(character_id=character_id, spell_id=spell_id))
    return result.scalars().first()

async def add_spell_to_character(
    db: AsyncSession, *, character_id: int, spell_association_in: CharacterSpellCreate
) -> CharacterSpellModel:
    spell_def = await db.get(SpellModel, spell_association_in.spell_id)
    if not spell_def: raise ValueError(f"Spell definition with ID {spell_association_in.spell_id} not found")
    existing_assoc = await get_character_spell_association(db, character_id=character_id, spell_id=spell_association_in.spell_id)
    if existing_assoc:
        changed = False
        if spell_association_in.is_known is not None and existing_assoc.is_known != spell_association_in.is_known: existing_assoc.is_known = spell_association_in.is_known; changed = True
        if spell_association_in.is_prepared is not None and existing_assoc.is_prepared != spell_association_in.is_prepared: existing_assoc.is_prepared = spell_association_in.is_prepared; changed = True
        if not changed: return await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == existing_assoc.id)).scalars().first()
        db_character_spell = existing_assoc
    else: db_character_spell = CharacterSpellModel(character_id=character_id, spell_id=spell_association_in.spell_id, is_known=spell_association_in.is_known if spell_association_in.is_known is not None else False, is_prepared=spell_association_in.is_prepared if spell_association_in.is_prepared is not None else False)
    db.add(db_character_spell); await db.commit(); await db.refresh(db_character_spell)
    result_with_spell_def = await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == db_character_spell.id))
    return result_with_spell_def.scalars().first()

async def update_character_spell_association(
    db: AsyncSession, *, character_id: int, spell_id: int, spell_association_update_in: CharacterSpellUpdate
) -> Optional[CharacterSpellModel]:
    db_char_spell = await get_character_spell_association(db, character_id=character_id, spell_id=spell_id)
    if not db_char_spell: return None
    update_data = spell_association_update_in.model_dump(exclude_unset=True)
    if not update_data: return await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == db_char_spell.id)).scalars().first()
    for field, value in update_data.items(): setattr(db_char_spell, field, value)
    db.add(db_char_spell); await db.commit(); await db.refresh(db_char_spell)
    result_with_spell_def = await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter(CharacterSpellModel.id == db_char_spell.id))
    return result_with_spell_def.scalars().first()

async def remove_spell_from_character(
    db: AsyncSession, *, character_id: int, spell_id: int
) -> Optional[CharacterSpellModel]:
    db_char_spell_to_delete = await db.execute(select(CharacterSpellModel).options(selectinload(CharacterSpellModel.spell_definition)).filter_by(character_id=character_id, spell_id=spell_id))
    db_character_spell = db_char_spell_to_delete.scalars().first()
    if db_character_spell: await db.delete(db_character_spell); await db.commit(); return db_character_spell
    return None

async def apply_sorcerer_spell_selections(
    db: AsyncSession, *, character: CharacterModel, spell_selection: SorcererSpellSelectionRequest
) -> CharacterModel:
    if not character.character_class or character.character_class.lower() != "sorcerer": raise ValueError("This spell selection process is only for Sorcerers.")
    if character.level_up_status != "pending_spells": raise ValueError(f"Character is not pending spell selection. Current status: {character.level_up_status}")
    char_level = character.level
    pre_selection_known_spells_q = await db.execute(select(CharacterSpellModel.spell_id).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level > 0))
    pre_selection_known_spell_ids = {row[0] for row in pre_selection_known_spells_q.all()}
    current_known_leveled_spells_count = len(pre_selection_known_spell_ids)
    target_cantrips_at_new_level, target_leveled_spells_at_new_level = SORCERER_SPELLS_KNOWN_TABLE.get(char_level, (0, 0))
    max_spell_level_learnable = get_sorcerer_max_spell_level_can_learn(char_level)
    if spell_selection.spell_to_replace_id is not None and spell_selection.replacement_spell_id is not None:
        if spell_selection.spell_to_replace_id == spell_selection.replacement_spell_id: raise ValueError("Cannot replace a spell with itself.")
        spell_to_replace_model = await db.get(SpellModel, spell_selection.spell_to_replace_id);
        if not spell_to_replace_model or spell_to_replace_model.level == 0: raise ValueError(f"Spell to replace (ID: {spell_selection.spell_to_replace_id}) is cantrip or non-existent.")
        if spell_selection.spell_to_replace_id not in pre_selection_known_spell_ids: raise ValueError(f"Spell to replace (ID: {spell_selection.spell_to_replace_id}) not currently known.")
        replacement_spell_model = await db.get(SpellModel, spell_selection.replacement_spell_id)
        if not replacement_spell_model: raise ValueError(f"Replacement spell ID {spell_selection.replacement_spell_id} not found.")
        if replacement_spell_model.level == 0 or replacement_spell_model.level > max_spell_level_learnable: raise ValueError(f"Replacement spell '{replacement_spell_model.name}' invalid level.")
        if not (replacement_spell_model.dnd_classes and "sorcerer" in [c.lower() for c in replacement_spell_model.dnd_classes]): raise ValueError(f"Replacement spell '{replacement_spell_model.name}' not Sorcerer spell.")
        already_knows_replacement = await get_character_spell_association(db, character_id=character.id, spell_id=replacement_spell_model.id)
        if already_knows_replacement and already_knows_replacement.is_known and replacement_spell_model.id != spell_selection.spell_to_replace_id : raise ValueError(f"Already knows replacement spell '{replacement_spell_model.name}'.")
        await remove_spell_from_character(db=db, character_id=character.id, spell_id=spell_selection.spell_to_replace_id)
        replacement_create_schema = CharacterSpellCreate(spell_id=replacement_spell_model.id, is_known=True, is_prepared=True)
        await add_spell_to_character(db=db, character_id=character.id, spell_association_in=replacement_create_schema)
        pre_selection_known_spell_ids.remove(spell_selection.spell_to_replace_id); pre_selection_known_spell_ids.add(replacement_spell_model.id)
    current_known_cantrips_q = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level == 0))
    current_known_cantrips_count = current_known_cantrips_q.scalar_one_or_none() or 0
    num_new_cantrips_to_choose = target_cantrips_at_new_level - current_known_cantrips_count
    if spell_selection.chosen_cantrip_ids_on_level_up:
        if len(spell_selection.chosen_cantrip_ids_on_level_up) != num_new_cantrips_to_choose: raise ValueError(f"Should choose {num_new_cantrips_to_choose} new cantrip(s). Provided: {len(spell_selection.chosen_cantrip_ids_on_level_up)}.")
        for spell_id in spell_selection.chosen_cantrip_ids_on_level_up:
            cantrip_def = await db.get(SpellModel, spell_id)
            if not cantrip_def or cantrip_def.level != 0: raise ValueError(f"Invalid cantrip ID {spell_id}.")
            if not (cantrip_def.dnd_classes and "sorcerer" in [c.lower() for c in cantrip_def.dnd_classes]): raise ValueError(f"Spell ID {spell_id} not Sorcerer cantrip.")
            already_knows_cantrip = await get_character_spell_association(db, character_id=character.id, spell_id=cantrip_def.id)
            if already_knows_cantrip and already_knows_cantrip.is_known: raise ValueError(f"Already knows cantrip '{cantrip_def.name}'.")
            cantrip_create_schema = CharacterSpellCreate(spell_id=cantrip_def.id, is_known=True, is_prepared=True)
            await add_spell_to_character(db=db, character_id=character.id, spell_association_in=cantrip_create_schema)
    elif num_new_cantrips_to_choose > 0: raise ValueError(f"Must choose {num_new_cantrips_to_choose} new cantrip(s).")
    current_known_leveled_spells_q_after_swap = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level > 0))
    current_known_leveled_spells_count_after_swap = current_known_leveled_spells_q_after_swap.scalar_one_or_none() or 0
    num_new_leveled_spells_to_choose = target_leveled_spells_at_new_level - current_known_leveled_spells_count_after_swap
    if spell_selection.new_leveled_spell_ids:
        if len(spell_selection.new_leveled_spell_ids) != num_new_leveled_spells_to_choose: raise ValueError(f"Should choose {num_new_leveled_spells_to_choose} new leveled spell(s). Provided: {len(spell_selection.new_leveled_spell_ids)}.")
        for spell_id in spell_selection.new_leveled_spell_ids:
            new_spell_to_learn_model = await db.get(SpellModel, spell_id)
            if not new_spell_to_learn_model: raise ValueError(f"New spell ID {spell_id} not found.")
            if new_spell_to_learn_model.level == 0 or new_spell_to_learn_model.level > max_spell_level_learnable: raise ValueError(f"New spell '{new_spell_to_learn_model.name}' invalid level.")
            if not (new_spell_to_learn_model.dnd_classes and "sorcerer" in [c.lower() for c in new_spell_to_learn_model.dnd_classes]): raise ValueError(f"New spell '{new_spell_to_learn_model.name}' not Sorcerer spell.")
            already_knows_new_spell = await get_character_spell_association(db, character_id=character.id, spell_id=new_spell_to_learn_model.id)
            if already_knows_new_spell and already_knows_new_spell.is_known: raise ValueError(f"Already knows new spell '{new_spell_to_learn_model.name}'.")
            new_spell_create_schema = CharacterSpellCreate(spell_id=new_spell_to_learn_model.id, is_known=True, is_prepared=True)
            await add_spell_to_character(db=db, character_id=character.id, spell_association_in=new_spell_create_schema)
    elif num_new_leveled_spells_to_choose > 0: raise ValueError(f"Must choose {num_new_leveled_spells_to_choose} new leveled spell(s).")
    await db.commit(); await db.refresh(character) 
    final_known_cantrips_q = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level == 0))
    final_known_cantrips_count = final_known_cantrips_q.scalar_one_or_none() or 0
    if final_known_cantrips_count != target_cantrips_at_new_level: raise ValueError(f"Incorrect final cantrips known ({final_known_cantrips_count}). Expected: {target_cantrips_at_new_level}.")
    final_known_leveled_spells_q = await db.execute(select(func.count(CharacterSpellModel.id)).join(SpellModel).filter(CharacterSpellModel.character_id == character.id, CharacterSpellModel.is_known == True, SpellModel.level > 0))
    final_known_leveled_spells_count = final_known_leveled_spells_q.scalar_one_or_none() or 0
    if final_known_leveled_spells_count != target_leveled_spells_at_new_level: raise ValueError(f"Incorrect final leveled spells known ({final_known_leveled_spells_count}). Expected: {target_leveled_spells_at_new_level}.")

    character.level_up_status = await _get_next_level_up_status(character, db)

    print(f"Character {character.name} Sorcerer spell selection complete. Level up status: {character.level_up_status}")
    db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)

# --- Hit Dice and Death Save functions ---
async def spend_character_hit_die(
    db: AsyncSession, *, character: CharacterModel, dice_roll_result: int
) -> CharacterModel:
    if character.hit_dice_remaining is None or character.hit_dice_remaining <= 0:
        raise ValueError("No hit dice remaining to spend.")
    if not character.hit_die_type:
        raise ValueError("Character hit_die_type is not set.")
    con_modifier = calculate_ability_modifier(character.constitution)
    hp_healed = max(1, dice_roll_result + con_modifier)
    character.hit_dice_remaining -= 1
    current_hp = character.hit_points_current if character.hit_points_current is not None else 0
    max_hp = character.hit_points_max if character.hit_points_max is not None else current_hp
    character.hit_points_current = min(current_hp + hp_healed, max_hp)
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def record_death_save(
    db: AsyncSession, *, character: CharacterModel, success: bool
) -> CharacterModel:
    if success:
        current_successes = character.death_save_successes if character.death_save_successes is not None else 0
        character.death_save_successes = min(current_successes + 1, 3)
    else:
        current_failures = character.death_save_failures if character.death_save_failures is not None else 0
        character.death_save_failures = min(current_failures + 1, 3)
    if character.death_save_successes >= 3 or character.death_save_failures >= 3:
        print(f"Character {character.name} death save resolved: Successes={character.death_save_successes}, Failures={character.death_save_failures}. Resetting saves.")
        character.death_save_successes = 0
        character.death_save_failures = 0
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

async def reset_death_saves(db: AsyncSession, *, character: CharacterModel) -> CharacterModel:
    character.death_save_successes = 0
    character.death_save_failures = 0
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return await get_character(db, character.id)

# --- Admin Function for setting character progression ---
async def admin_update_character_progression(
    db: AsyncSession, *, character: CharacterModel, progression_in: AdminCharacterProgressionUpdate
) -> CharacterModel:
    updated = False
    if progression_in.level is not None:
        max_level = 50 if character.is_ascended_tier else 30
        if not (1 <= progression_in.level <= max_level):
            raise ValueError(f"Admin: Target level ({progression_in.level}) is outside the allowed range (1-{max_level}) for this character's tier.")
        character.level = progression_in.level
        character.experience_points = get_xp_for_level(character.level)
        if character.hit_die_type and character.constitution is not None:
            con_mod = calculate_ability_modifier(character.constitution)
            new_max_hp = character.hit_die_type + con_mod 
            if character.level > 1:
                for _lvl in range(2, character.level + 1):
                    new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
            character.hit_points_max = new_max_hp
            character.hit_points_current = new_max_hp
        character.hit_dice_total = character.level
        character.hit_dice_remaining = character.level
        character.level_up_status = None 
        updated = True
    elif progression_in.experience_points is not None:
        character.experience_points = progression_in.experience_points
        new_level = get_level_for_xp(character.experience_points, character.is_ascended_tier)
        if new_level != character.level: 
            character.level = new_level
            character.hit_dice_total = new_level
            character.hit_dice_remaining = new_level
            if character.hit_die_type and character.constitution is not None:
                con_mod = calculate_ability_modifier(character.constitution)
                new_max_hp = character.hit_die_type + con_mod
                if character.level > 1:
                    for _lvl in range(2, character.level + 1):
                        new_max_hp += max(1, (character.hit_die_type // 2) + 1 + con_mod)
                character.hit_points_max = new_max_hp
                character.hit_points_current = new_max_hp
            character.level_up_status = None
        updated = True
    if updated:
        db.add(character); await db.commit(); await db.refresh(character)
    return await get_character(db, character.id)


