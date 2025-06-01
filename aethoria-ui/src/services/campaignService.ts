// Path: src/services/campaignService.ts
import type { Campaign } from '../types/campaign';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const campaignService = {
  getCampaigns: async (token: string, asDM: boolean): Promise<Campaign[]> => {
    // The backend endpoint is GET /campaigns/
    // It uses a query parameter `view_as_dm=true` or `view_as_dm=false` (or omit for false)
    const url = new URL(`${API_BASE_URL}/campaigns/`);
    if (asDM) {
      url.searchParams.append('view_as_dm', 'true');
    }
    // If view_as_dm is false, we don't need to append it as it's the default behavior
    // or your backend might require view_as_dm=false explicitly.
    // Let's assume omitting it defaults to player view or view_as_dm=false is also fine.

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

  // We will add createCampaign, getCampaignById, updateCampaign, etc. here later
};