// Path: src/types/character.ts
import type { CharacterSkill } from './skill'; 
import type { CharacterItem } from './item';   
import type { CharacterSpell } from './spell'; 

export type { CharacterSkill, SkillDefinition } from './skill'; 
export type { CharacterItem, ItemDefinition, FrontendItemTypeEnumObject } from './item';   
export type { CharacterSpell, SpellDefinition, FrontendSchoolOfMagicEnumObject } from './spell'; 
export interface Character {
  id: number;
  user_id: number; 
  name: string;
  race: string | null;
  character_class: string | null;
  roguish_archetype: string | null; 

  is_ascended_tier: boolean;
  level: number; 
  experience_points: number | null;

  alignment: string | null;
  background_story: string | null;
  appearance_description: string | null;

  strength: number; 
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;

  hit_points_max: number | null; 
  hit_points_current: number | null; 

  armor_class: number | null; 

  hit_die_type: number | null;
  hit_dice_total: number;
  hit_dice_remaining: number;

  death_save_successes: number;
  death_save_failures: number;

  level_up_status: string | null;

  created_at: string; 
  updated_at: string; 

  skills: CharacterSkill[];       
  inventory_items: CharacterItem[]; 
  known_spells: CharacterSpell[];   
}

// These are other types that CAN live in character.ts as they are related to character actions/responses
export interface CharacterHPLevelUpResponse {
    character: Character; 
    hp_gained: number;
    level_up_message: string;
}

export interface ExpertiseSelectionRequest {
  expert_skill_ids: number[];
}

export interface ASISelectionRequest { // Assuming this was defined earlier, if not add it
    stat_increases: Record<string, number>; // e.g. { "strength": 1, "dexterity": 1 }
}

export interface SorcererSpellSelectionRequest { // Assuming this was defined earlier
    new_leveled_spell_ids: number[] | null;
    spell_to_replace_id: number | null;
    replacement_spell_id: number | null;
    chosen_cantrip_ids_on_level_up: number[] | null;
}

// --- NEW TYPE for Rogue Archetype Selection Request ---
// This should match the Pydantic schema RogueArchetypeSelectionRequest on the backend
// which expects archetype_name: RoguishArchetypeEnum
// On the frontend, we'll send the string value of the enum.
export interface RogueArchetypeSelectionRequest {
  archetype_name: string; // e.g., "Thief", "Assassin", "Arcane Trickster"
}
// --- END NEW TYPE ---


