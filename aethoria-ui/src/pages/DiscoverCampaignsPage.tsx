// Path: src/pages/DiscoverCampaignsPage.tsx
import React, { useEffect, useState } from 'react';
import { Link /*, useNavigate */ } from 'react-router-dom'; // useNavigate commented out
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { Campaign } from '../types/campaign';
import ThemedButton from '../components/common/ThemedButton';
import styles from './DiscoverCampaignsPage.module.css'; // Using its own CSS module



const DiscoverCampaignsPage: React.FC = () => {
  const auth = useAuth();
  // const navigate = useNavigate(); // Commented out as not used
  const [discoverableCampaigns, setDiscoverableCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [requestStatus, setRequestStatus] = useState<Record<number, string>>({});

  useEffect(() => {
    const fetchCampaigns = async () => {
      if (auth?.token && auth.isAuthenticated) {
        setIsLoading(true);
        setError(null);
        try {
          const campaigns = await campaignService.getDiscoverableCampaigns(auth.token);
          setDiscoverableCampaigns(campaigns);
        } catch (err: any) {
          setError(err.message || "Could not load discoverable campaigns.");
        } finally {
          setIsLoading(false);
        }
      } else if (!auth?.isLoading) {
        setError("You must be logged in to discover campaigns.");
        setIsLoading(false);
      }
    };

    if (!auth?.isLoading) {
        fetchCampaigns();
    }
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]);

  const handleRequestToJoin = async (campaignId: number) => {
    if (!auth?.token) {
      setError("Authentication required.");
      return;
    }
    setRequestStatus(prev => ({ ...prev, [campaignId]: "Requesting..." }));
    try {
      await campaignService.requestToJoinCampaign(auth.token, campaignId);
      setRequestStatus(prev => ({ ...prev, [campaignId]: "Requested!" }));
      alert("Your request to join has been sent!");
    } catch (err: any) {
      console.error(`Failed to request join for campaign ${campaignId}:`, err);
      setRequestStatus(prev => ({ ...prev, [campaignId]: `Error: ${err.message || 'Failed'}` }));
    }
  };

  if (isLoading && !discoverableCampaigns.length && !error) { 
    return <div className={styles.pageStyle}><p>Searching for open campaigns...</p></div>;
  }

  if (!auth?.isAuthenticated && !auth?.isLoading) {
    return (
      <div className={styles.pageStyle} style={{textAlign: 'center'}}>
        <p>Please <Link to="/login" style={{color: 'var(--ink-color-dark)'}}>log in</Link> to discover campaigns.</p>
      </div>
    );
  }
  
  if (error && !discoverableCampaigns.length) { // Only show main error if no campaigns loaded
    return <div className={styles.pageStyle}><p className={styles.errorText}>{error}</p></div>;
  }

  return (
    <div className={styles.pageStyle}>
      {/* Outer div for the wavy edge and textured background */}
      <div className={styles.sheetContainerWithWavyEffect}> 
        {/* Inner div for the actual, non-distorted content */}
        <div className={styles.sheetContent}>
            <h1 className={styles.title}>Discover Open Campaigns</h1>

            {isLoading && discoverableCampaigns.length > 0 && <p className={styles.infoText}>Refreshing campaign list...</p>}
            
            {!isLoading && discoverableCampaigns.length === 0 && !error && (
            <p className={styles.infoText}>
                No campaigns are currently open for recruitment. Check back soon!
            </p>
            )}
            
            {/* Display general error if it occurred even if some campaigns might have loaded before (or if fetch fails) */}
            {error && <p className={styles.errorText}>{error}</p>}


            {discoverableCampaigns.length > 0 && (
            <ul className={styles.campaignList}>
                {discoverableCampaigns.map((campaign) => (
                <li key={campaign.id} className={styles.campaignItem}>
                    <h2 className={styles.campaignTitle}>{campaign.title}</h2>
                    <p className={styles.campaignDetail}>
                    <strong>DM:</strong> {campaign.dm?.username || 'Unknown Scribe'}
                    </p>
                    {campaign.description && (
                        <p className={styles.campaignDescription}>
                            {campaign.description}
                        </p>
                    )}
                    <p className={styles.campaignDetail}>
                    <strong>Max Players:</strong> {campaign.max_players || 'Not specified'} | 
                    <strong> Current Members:</strong> {campaign.members?.length || 0}
                    </p>
                    {campaign.next_session_utc && (
                    <p className={styles.campaignDetail}>
                        <strong>Next Session:</strong> {new Date(campaign.next_session_utc).toLocaleString()}
                    </p>
                    )}
                    <div className={styles.buttonContainer}>
                    <ThemedButton
                        onClick={() => handleRequestToJoin(campaign.id)}
                        disabled={!!requestStatus[campaign.id] && (requestStatus[campaign.id] === "Requesting..." || requestStatus[campaign.id] === "Requested!")}
                        variant={requestStatus[campaign.id] === "Requested!" ? undefined : "green"} // Corrected variant
                        runeSymbol={requestStatus[campaign.id] === "Requested!" ? "⏳" : "➕"}
                        tooltipText={
                            requestStatus[campaign.id] === "Requested!" ? "Request Sent (Pending Approval)" : 
                            requestStatus[campaign.id]?.startsWith("Error:") ? requestStatus[campaign.id] :
                            "Request to Join"
                        }
                    >
                        {requestStatus[campaign.id] ? requestStatus[campaign.id].split(":")[0] : "Request to Join"}
                    </ThemedButton>
                    </div>
                </li>
                ))}
            </ul>
            )}
        </div>
      </div>
    </div>
  );
};

export default DiscoverCampaignsPage;


