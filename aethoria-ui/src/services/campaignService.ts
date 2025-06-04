// Path: src/services/campaignService.ts
import type { Campaign } from '../types/campaign';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const campaignService = {
  getCampaigns: async (token: string, asDM: boolean): Promise<Campaign[]> => {
    const url = new URL(`${API_BASE_URL}/campaigns/`);
    if (asDM) {
      url.searchParams.append('view_as_dm', 'true');
    }
    // If view_as_dm is false, the backend endpoint /campaigns/ should return campaigns
    // where the user is a member (excluding those they DM if that's the backend logic).

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized: Session may have expired.');
      }
      throw new Error(`Failed to fetch campaigns (status: ${response.status})`);
    }
    return response.json() as Promise<Campaign[]>;
  },

  // --- NEW FUNCTION to get discoverable campaigns ---
  getDiscoverableCampaigns: async (token: string): Promise<Campaign[]> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/discoverable`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`, // Assuming this endpoint also requires auth
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized: Session may have expired.');
      }
      throw new Error(`Failed to fetch discoverable campaigns (status: ${response.status})`);
    }
    return response.json() as Promise<Campaign[]>;
  },
  // --- END NEW FUNCTION ---

  // Placeholder for requesting to join a campaign
  requestToJoinCampaign: async (token: string, campaignId: number): Promise<any> => { // Return type can be more specific later
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/members/request-join`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json', // Though body is empty, content-type might be expected
        },
        // No body needed for this specific request as per backend
    });

    if (!response.ok) {
        let errorDetail = `Request to join campaign failed: ${response.status}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                errorDetail = Array.isArray(errorData.detail) 
                    ? errorData.detail.map((e: any) => e.msg).join(', ') 
                    : errorData.detail;
            }
        } catch (e) { /* Ignore if error response is not JSON */ }
        
        if (response.status === 401) throw new Error('Unauthorized.');
        if (response.status === 403) throw new Error(errorDetail || 'Forbidden: You may already be a member or have a pending request.');
        if (response.status === 404) throw new Error('Campaign not found.');
        if (response.status === 409) throw new Error(errorDetail || 'Conflict: Request already exists or user is already a member.');
        throw new Error(errorDetail);
    }
    // Backend returns the CampaignMemberSchema on success (201 CREATED)
    return response.json(); 
  },

  // We will add createCampaign, getCampaignById, updateCampaign, etc. here later
};