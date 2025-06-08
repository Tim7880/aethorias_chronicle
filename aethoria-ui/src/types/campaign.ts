// Path: src/types/campaign.ts
import type { User } from './user'; 
import type { Character } from './character'; 

export type { CharacterSkill, SkillDefinition } from './skill'; 
export type { CharacterItem, ItemDefinition, FrontendItemTypeEnumObject } from './item';   
export type { CharacterSpell, SpellDefinition, FrontendSchoolOfMagicEnumObject } from './spell'; 
export type { User } from './user'; // Re-exporting User for clarity if CampaignBasicInfo uses it
export type { Character } from './character';
export interface CampaignBasicInfo {
  id: number;
  title: string;
  dm_user_id: number;
  dm?: Pick<User, 'id' | 'username'> | null; // <--- ADDED DM details here
}
export interface CampaignMember {
  id: number; 
  campaign_id: number; 
  user_id: number;
  character_id?: number | null; 
  status: string; 
  
  user?: Pick<User, 'id' | 'username'>; 
  character?: Pick<Character, 'id' | 'name' | 'character_class' | 'level' | 'race' | 'alignment'> | null; 
  campaign?: CampaignBasicInfo | null; // This now includes DM details via CampaignBasicInfo
  
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
}
