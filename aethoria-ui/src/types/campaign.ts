// Path: src/types/campaign.ts
import type { User } from './user'; // For DM and member user details
import type { Character } from './character'; // For member character details

// This interface represents a campaign member, including details for join requests
// It aligns with your preference for using Pick<>

export interface CampaignBasicInfo {
  id: number;
  title: string;
  dm_user_id: number; // Useful for context, matches backend CampaignBasicInfoSchema
}
export interface CampaignMember {
  id: number; // The ID of the CampaignMember record itself
  campaign_id: number; // Added for completeness, often useful
  user_id: number;
  character_id?: number | null; // Character used by the player in this campaign
  status: string; // e.g., "PENDING_APPROVAL", "ACTIVE", "REJECTED", "INACTIVE", "BANNED"
  
  // User details for the member/requester
  user?: Pick<User, 'id' | 'username'>; 
  
  // Character details for the member/requester, including fields DM needs for join requests
  character?: Pick<Character, 'id' | 'name' | 'character_class' | 'level' | 'race' | 'alignment'> | null; 
  campaign?: CampaignBasicInfo | null;
  joined_at: string; // Or request_sent_at, status_updated_at - ISO datetime string
}

// This interface should align with your backend's CampaignSchema response model
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
  
  dm?: Pick<User, 'id' | 'username'>; // DM's basic info
  members: CampaignMember[]; // List of members, now using the updated CampaignMember type
}

export interface PlayerCampaignJoinRequest {
  character_id?: number | null;
}