// Path: src/pages/CampaignManagementPage.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { Campaign, CampaignMember } from '../types/campaign';
import ThemedButton from '../components/common/ThemedButton';
import styles from './CampaignManagementPage.module.css'; // <--- IMPORTING ITS OWN CSS MODULE

const CampaignManagementPage: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const auth = useAuth();
  const navigate = useNavigate(); // Keep for navigation

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [joinRequests, setJoinRequests] = useState<CampaignMember[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<Record<number, string>>({});

  const loadCampaignData = useCallback(async () => {
    if (auth?.token && campaignId) {
      setIsLoading(true);
      setError(null);
      setActionStatus({});
      try {
        const id = parseInt(campaignId, 10);
        if (isNaN(id)) throw new Error("Invalid campaign ID in URL.");
        
        const campaignDetails = await campaignService.getCampaignById(auth.token, id);
        setCampaign(campaignDetails);

        if (campaignDetails && campaignDetails.dm_user_id !== auth.user?.id) {
          setError("You are not authorized to manage this campaign.");
          setTimeout(() => navigate('/dashboard'), 3000);
          return; 
        }
        
        const pendingRequests = await campaignService.getCampaignJoinRequests(auth.token, id);
        setJoinRequests(pendingRequests.filter(req => req.status === "PENDING_APPROVAL"));

      } catch (err: any) {
        setError(err.message || "Failed to load campaign management data.");
      } finally {
        setIsLoading(false);
      }
    } else if (!auth?.isLoading) {
      setError("Authentication required or campaign ID missing.");
      setIsLoading(false);
    }
  }, [auth?.token, auth?.user?.id, auth?.isLoading, campaignId, navigate]);

  useEffect(() => {
    if (!auth?.isLoading) { 
        loadCampaignData();
    }
  }, [auth?.isLoading, loadCampaignData]);

  const handleApproveRequest = async (requesterUserId: number) => {
    if (!auth?.token || !campaignId) return;
    const campaignIdNum = parseInt(campaignId, 10);
    setActionStatus(prev => ({ ...prev, [requesterUserId]: "Approving..."}));
    try {
      await campaignService.approveJoinRequest(auth.token, campaignIdNum, requesterUserId);
      setActionStatus(prev => ({ ...prev, [requesterUserId]: "Approved!"}));
      alert("Join request approved!");
      loadCampaignData(); 
    } catch (err: any) {
      console.error("Approval error:", err);
      const errorMessage = err.message || 'Failed to approve request.';
      setActionStatus(prev => ({ ...prev, [requesterUserId]: `Error: ${errorMessage}`}));
      setError(errorMessage); 
    }
  };

  const handleRejectRequest = async (requesterUserId: number) => {
    if (!auth?.token || !campaignId) return;
    const campaignIdNum = parseInt(campaignId, 10);
    setActionStatus(prev => ({ ...prev, [requesterUserId]: "Rejecting..."}));
    try {
      await campaignService.rejectJoinRequest(auth.token, campaignIdNum, requesterUserId);
      setActionStatus(prev => ({ ...prev, [requesterUserId]: "Rejected"}));
      alert("Join request rejected.");
      setJoinRequests(prev => prev.filter(req => req.user?.id !== requesterUserId));
    } catch (err: any) {
      console.error("Rejection error:", err);
      const errorMessage = err.message || 'Failed to reject request.';
      setActionStatus(prev => ({ ...prev, [requesterUserId]: `Error: ${errorMessage}`}));
      setError(errorMessage);
    }
  };

  if (isLoading && !campaign) {
    return <div className={styles.pageStyle}><p>Loading campaign management...</p></div>;
  }

  if (error && !campaign) { 
    return <div className={styles.pageStyle}><p className={styles.errorText}>{error}</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  
  if (!campaign) { 
     return <div className={styles.pageStyle}><p>Campaign data could not be loaded or found.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  
  if (error && campaign && campaign.dm_user_id !== auth?.user?.id) {
     return <div className={styles.pageStyle}><p className={styles.errorText}>{error}</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }

  return (
    <div className={styles.pageStyle}>
      <div className={styles.sheetContainerWithWavyEffect}> 
        <div className={styles.sheetContent}>
          <header style={{textAlign: 'center', marginBottom: '20px'}}>
            <h1 className={styles.title}>{campaign.title}</h1>
            <p style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-medium)'}}>
              Campaign Management (DM: {campaign.dm?.username || 'You'})
            </p>
          </header>

          {campaign.description && (
            <div className={styles.box} style={{marginBottom: '25px'}}>
              <h2 className={styles.sectionTitle}>Campaign Description</h2>
              <p className={styles.campaignDescription}>
                {campaign.description}
              </p>
            </div>
          )}

          <div className={styles.box}>
            <h2 className={styles.sectionTitle}>Pending Join Requests ({joinRequests.length})</h2>
            {isLoading && !joinRequests.length && <p>Loading requests...</p>}
            {!isLoading && joinRequests.length === 0 && (
              <p className={styles.infoTextLeft}>No pending join requests at this time.</p>
            )}
            {joinRequests.length > 0 && (
              <ul style={{listStyle: 'none', padding: 0}}>
                {joinRequests.map(request => (
                  <li key={request.id} className={styles.requestItem}>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.6em', margin: '0 0 10px 0'}}>
                      Request from: {request.user?.username || 'Unknown User'}
                    </h3>
                    {request.character && (
                      <div className={styles.requestCharacterInfo}>
                        <p><strong>Character:</strong> {request.character.name}</p>
                        <p>
                          Lvl {request.character.level} {request.character.race} {request.character.character_class}
                        </p>
                        <p>Alignment: {request.character.alignment || 'N/A'}</p>
                      </div>
                    )}
                    {!request.character && (
                      <p className={styles.requestCharacterInfo}>No character specified for this request.</p>
                    )}
                    <div className={styles.requestActions}>
                      <ThemedButton
                        onClick={() => handleApproveRequest(request.user_id)}
                        disabled={!!actionStatus[request.user_id] && (actionStatus[request.user_id] === "Approving..." || actionStatus[request.user_id] === "Approved!")}
                        variant="green"
                        runeSymbol="✔"
                        tooltipText="Approve Request"
                        style={{fontSize: '0.9em', padding: '6px 12px'}}
                      >
                        {actionStatus[request.user_id] === "Approving..." ? "Approving..." : 
                         actionStatus[request.user_id] === "Approved!" ? "Approved" : "Approve"}
                      </ThemedButton>
                      <ThemedButton
                        onClick={() => handleRejectRequest(request.user_id)}
                        disabled={!!actionStatus[request.user_id] && (actionStatus[request.user_id] === "Rejecting..." || actionStatus[request.user_id] === "Rejected!")}
                        variant="red"
                        runeSymbol="✖"
                        tooltipText="Reject Request"
                        style={{fontSize: '0.9em', padding: '6px 12px'}}
                      >
                         {actionStatus[request.user_id] === "Rejecting..." ? "Rejecting..." : 
                          actionStatus[request.user_id] === "Rejected" ? "Rejected" : "Reject"}
                      </ThemedButton>
                    </div>
                     {actionStatus[request.user_id] && actionStatus[request.user_id].startsWith("Error:") && (
                        <p className={styles.errorText} style={{fontSize: '0.8em', marginTop: '5px', textAlign:'right'}}>{actionStatus[request.user_id]}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          {error && <p className={styles.errorText} style={{marginTop: '20px'}}>{error}</p>}

          <div style={{marginTop: '30px', textAlign: 'center'}}>
              <Link to="/dashboard" style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-dark)', fontSize: '1.1em', padding: '8px 15px', border: '1px solid var(--ink-color-medium)', borderRadius: '4px', textDecoration: 'none'}}>
                  Return to Dashboard
              </Link>
          </div>

        </div>
      </div>
    </div>
  );
};

export default CampaignManagementPage;


