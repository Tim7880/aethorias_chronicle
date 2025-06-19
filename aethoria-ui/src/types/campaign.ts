// Path: src/types/campaign.ts
import type { User } from './user'; 
import type { Character } from './character'; 

// --- Re-exports (Kept as is from your file) ---
export type { CharacterSkill, SkillDefinition } from './skill'; 
export type { CharacterItem, ItemDefinition, FrontendItemTypeEnumObject } from './item';   
export type { CharacterSpell, SpellDefinition, FrontendSchoolOfMagicEnumObject } from './spell'; 
export type { User } from './user';
export type { Character } from './character';

// --- Campaign-related interfaces ---

export interface CampaignBasicInfo {
  id: number;
  title: string;
  dm_user_id: number;
  dm?: Pick<User, 'id' | 'username'> | null;
}

export interface CampaignMember {
  id: number; 
  campaign_id: number; 
  user_id: number;
  character_id?: number | null; 
  status: string; 
  user?: Pick<User, 'id' | 'username'>; 
  character?: Pick<Character, 'id' | 'name' | 'character_class' | 'level' | 'race' | 'alignment'> | null; 
  campaign?: CampaignBasicInfo | null;
  joined_at: string; 
}

export interface Campaign {
  id: number;
  title: string;
  description?: string | null;
  dm_user_id: number;
  banner_image_url?: string | null;
  max_players?: number | null;
  next_session_utc?: string | null; 
  house_rules?: string | null;
  is_open_for_recruitment: boolean;
  session_notes?: string | null; // <--- ADDED session_notes
  created_at: string; 
  updated_at: string; 
  dm?: Pick<User, 'id' | 'username'>; 
  members: CampaignMember[]; 
}

export interface PlayerCampaignJoinRequest {
  character_id?: number | null;
}

export interface CampaignCreatePayload {
  title: string;
  description?: string | null;
  banner_image_url?: string | null;
  max_players?: number | null;
  next_session_utc?: string | null; 
  house_rules?: string | null;
  is_open_for_recruitment?: boolean;
  session_notes?: string | null; // <--- ADDED session_notes
}

// --- NEW: Interface for the Update Campaign form payload ---
// This aligns with your backend CampaignUpdate Pydantic schema
export interface CampaignUpdatePayload {
    title?: string;
    description?: string | null;
    banner_image_url?: string | null;
    max_players?: number | null;
    next_session_utc?: string | null; 
    house_rules?: string | null;
    is_open_for_recruitment?: boolean;
    session_notes?: string | null;
}
// --- END NEW ---
export interface InitiativeEntry {
  id: number;
  session_id: number;
  character_id?: number | null;
  monster_name?: string | null;
  initiative_roll: number;
  // The backend can populate the character details for us
  character?: Pick<Character, 'id' | 'name'> | null;
}

export interface CampaignSession {
  id: number;
  campaign_id: number;
  is_active: boolean;
  map_state?: Record<string, any> | null;
  initiative_entries: InitiativeEntry[];
  active_initiative_entry_id: number | null;
}

export type EncounterState = CampaignSession;