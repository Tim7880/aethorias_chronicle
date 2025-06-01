// Path: src/types/campaign.ts
import type { User } from './user'; // For DM and member user details
import type { Character } from './character'; // For member character details

// Simplified CampaignMember for frontend display within a Campaign list
// This should align with your backend's CampaignMemberSchema
export interface CampaignMemberSummary {
  id: number;
  user_id: number;
  character_id?: number | null;
  status: string; // e.g., "ACTIVE", "PENDING_APPROVAL"
  user?: Pick<User, 'id' | 'username'>; // Only essential user info
  character?: Pick<Character, 'id' | 'name' | 'character_class' | 'level'>; // Essential char info
  joined_at: string;
}

// This should align with your backend's CampaignSchema response model
export interface Campaign {
  id: number;
  title: string;
  description?: string | null;
  dm_user_id: number;
  banner_image_url?: string | null;
  max_players?: number | null;
  next_session_utc?: string | null; // ISO datetime string
  house_rules?: string | null;
  is_open_for_recruitment: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string

  dm?: Pick<User, 'id' | 'username'>; // DM's basic info
  members: CampaignMemberSummary[]; // List of members
}