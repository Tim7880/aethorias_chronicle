// Path: src/services/campaignService.ts
import type { Campaign, CampaignMember, PlayerCampaignJoinRequest, CampaignCreatePayload } from '../types/campaign'; // Added PlayerCampaignJoinRequest

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const campaignService = {
  getCampaigns: async (token: string, asDM: boolean): Promise<Campaign[]> => {
    const url = new URL(`${API_BASE_URL}/campaigns/`);
    if (asDM) {
      url.searchParams.append('view_as_dm', 'true');
    }

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

  getDiscoverableCampaigns: async (token: string): Promise<Campaign[]> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/discoverable`, {
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
      throw new Error(`Failed to fetch discoverable campaigns (status: ${response.status})`);
    }
    return response.json() as Promise<Campaign[]>;
  },

  requestToJoinCampaign: async (
    token: string, 
    campaignId: number, 
    payload: PlayerCampaignJoinRequest // Accept payload
  ): Promise<CampaignMember> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/join-requests`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json', 
        },
        body: JSON.stringify(payload), // Send the payload as JSON body
    });

    if (!response.ok) {
        let errorDetail = `Request to join campaign failed: ${response.status}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                errorDetail = Array.isArray(errorData.detail) 
                    ? errorData.detail.map((e: any) => e.msg || 'Unknown error detail').join(', ') 
                    : String(errorData.detail);
            }
        } catch (e) { /* Ignore if error response is not JSON */ }
        
        if (response.status === 401) throw new Error('Unauthorized.');
        if (response.status === 403) throw new Error(errorDetail || 'Forbidden: Cannot request to join this campaign.');
        if (response.status === 404) throw new Error('Campaign not found.');
        if (response.status === 409) throw new Error(errorDetail || 'Conflict: Request already exists or user is already a member.'); // 409 for conflict
        if (response.status === 422) throw new Error(errorDetail || 'Unprocessable Entity: Invalid data provided.'); // Handle 422 specifically
        throw new Error(errorDetail);
    }
    return response.json() as Promise<CampaignMember>; 
  },

  getCampaignJoinRequests: async (token: string, campaignId: number): Promise<CampaignMember[]> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/join-requests`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) throw new Error('Unauthorized: Session may have expired.');
      if (response.status === 403) throw new Error('Forbidden: You are not authorized to view join requests.');
      if (response.status === 404) throw new Error('Campaign not found.');
      throw new Error(`Failed to fetch join requests (status: ${response.status})`);
    }
    return response.json() as Promise<CampaignMember[]>;
  },

  getCampaignById: async (token: string, campaignId: number): Promise<Campaign> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
        let errorDetail = `Failed to fetch campaign ${campaignId}: ${response.status}`;
        try { const errorData = await response.json(); if (errorData && errorData.detail) { errorDetail = Array.isArray(errorData.detail) ? errorData.detail.map((e: any) => e.msg).join(', ') : String(errorData.detail); }} catch (e) {}
        if (response.status === 404) throw new Error("Campaign not found.");
        if (response.status === 401) throw new Error("Unauthorized.");
        if (response.status === 403) throw new Error("Forbidden: You do not have permission to view this campaign.");
        throw new Error(errorDetail);
    }
    return response.json() as Promise<Campaign>;
  },

  approveJoinRequest: async (token: string, campaignId: number, userIdOfRequester: number): Promise<CampaignMember> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/join-requests/${userIdOfRequester}/approve`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
        let errorDetail = `Approving join request failed: ${response.status}`;
        try { const errorData = await response.json(); if (errorData && errorData.detail) { errorDetail = Array.isArray(errorData.detail) ? errorData.detail.map((e: any) => e.msg).join(', ') : String(errorData.detail); }} catch (e) {}
        if (response.status === 400) throw new Error(errorDetail || 'Bad Request (e.g., campaign full).');
        if (response.status === 401) throw new Error('Unauthorized.');
        if (response.status === 403) throw new Error('Forbidden: Only DM can approve.');
        if (response.status === 404) throw new Error('Campaign or join request not found.');
        throw new Error(errorDetail);
    }
    return response.json() as Promise<CampaignMember>;
  },

  rejectJoinRequest: async (token: string, campaignId: number, userIdOfRequester: number): Promise<CampaignMember> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/join-requests/${userIdOfRequester}/reject`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
        let errorDetail = `Rejecting join request failed: ${response.status}`;
        try { const errorData = await response.json(); if (errorData && errorData.detail) { errorDetail = Array.isArray(errorData.detail) ? errorData.detail.map((e: any) => e.msg).join(', ') : String(errorData.detail); }} catch (e) {}
        if (response.status === 401) throw new Error('Unauthorized.');
        if (response.status === 403) throw new Error('Forbidden: Only DM can reject.');
        if (response.status === 404) throw new Error('Campaign or join request not found.');
        throw new Error(errorDetail);
    }
    return response.json() as Promise<CampaignMember>;
  },
  
  getActiveCampaignMembers: async (token: string, campaignId: number): Promise<CampaignMember[]> => {
    const url = new URL(`${API_BASE_URL}/campaigns/${campaignId}/members`); // Assuming trailing slash for consistency
    url.searchParams.append('status', 'active'); // Filter by ACTIVE status

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
      if (response.status === 403) {
        throw new Error('Forbidden: You are not authorized to view members of this campaign.');
      }
      if (response.status === 404) {
        throw new Error('Campaign not found.');
      }
      throw new Error(`Failed to fetch active campaign members (status: ${response.status})`);
    }
    return response.json() as Promise<CampaignMember[]>;
  },
  
  getMyCampaignMemberships: async (token: string): Promise<CampaignMember[]> => {
    const response = await fetch(`${API_BASE_URL}/users/me/campaign-memberships/`, {
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
      throw new Error(`Failed to fetch your campaign memberships (status: ${response.status})`);
    }
    return response.json() as Promise<CampaignMember[]>;
  },

  cancelJoinRequest: async (token: string, campaignMemberId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/campaign-members/${campaignMemberId}/my-request`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      let errorDetail = `Canceling join request failed: ${response.status}`;
      try {
          const errorData = await response.json();
          if (errorData && errorData.detail) {
              errorDetail = Array.isArray(errorData.detail) 
                  ? errorData.detail.map((e: any) => e.msg || 'Unknown error detail').join(', ') 
                  : String(errorData.detail);
          }
      } catch (e) { /* Ignore if error response is not JSON */ }
      
      if (response.status === 401) throw new Error('Unauthorized.');
      if (response.status === 403) throw new Error(errorDetail || 'Forbidden: You are not authorized to cancel this request.');
      if (response.status === 404) throw new Error('Join request not found.');
      throw new Error(errorDetail);
    }
   
    return;
  },
  createCampaign: async (token: string, payload: CampaignCreatePayload): Promise<Campaign> => {
    const response = await fetch(`${API_BASE_URL}/campaigns/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        let errorDetail = `Campaign creation failed: ${response.status}`;
        try {
            const errorData = await response.json();
            if (errorData && errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorDetail = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join('; ');
                } else {
                    errorDetail = errorData.detail;
                }
            }
        } catch (e) { /* Ignore */ }
        throw new Error(errorDetail);
    }
    return response.json() as Promise<Campaign>;
  }
  
};


