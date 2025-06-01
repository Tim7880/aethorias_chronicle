// Path: src/types/character.ts
import type { CharacterSkill } from './skill'; 
import type { CharacterItem } from './item';   
import type { CharacterSpell } from './spell'; 

// This interface should align with your backend's CharacterSchema response model,
// including all the fields we've added (ability scores, HP, HD, death saves, level up status, etc.)
export interface Character {
  id: number;
  user_id: number; // Owner of the character
  name: string;
  race: string | null;
  character_class: string | null;
  roguish_archetype: string | null; // Using string here, can map to RoguishArchetypeEnum on frontend if needed
                                    // Or import the enum if preferred for strict typing on frontend
  
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
  
  hit_die_type: number | null; // e.g., 6, 8, 10, 12
  hit_dice_total: number;
  hit_dice_remaining: number;

  death_save_successes: number;
  death_save_failures: number;
  
  level_up_status: string | null; // e.g., "pending_hp", "pending_asi", "pending_expertise", "pending_spells", "pending_archetype_selection"

  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string

  // Nested arrays of associated data, using the imported types
  skills: CharacterSkill[];       
  inventory_items: CharacterItem[]; 
  known_spells: CharacterSpell[];   
}

// Note: All placeholder or duplicate definitions for SkillDefinition, CharacterSkill,
// ItemDefinition, CharacterItem, SpellDefinition, and CharacterSpell
// have been removed from this file as they are now imported from their
// respective dedicated files (skill.ts, item.ts, spell.ts).