// Path: src/pages/CampaignViewPage.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { Campaign, CampaignMember } from '../types/campaign';
import ThemedButton from '../components/common/ThemedButton';
import styles from './CampaignViewPage.module.css';

const CampaignViewPage: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const auth = useAuth();
  const navigate = useNavigate(); // For redirecting after leaving
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isLeaving, setIsLeaving] = useState(false); // State for leave button

  const loadCampaignData = useCallback(async () => {
    if (auth?.token && campaignId) {
      setIsLoading(true);
      setError(null);
      try {
        const id = parseInt(campaignId, 10);
        if (isNaN(id)) throw new Error("Invalid campaign ID.");
        
        const campaignDetails = await campaignService.getCampaignById(auth.token, id);
        
        const isMember = campaignDetails.members.some(m => m.user_id === auth.user?.id && m.status === 'active');
        const isDm = campaignDetails.dm_user_id === auth.user?.id;
        
        if (!isMember && !isDm) {
          throw new Error("You are not authorized to view this campaign.");
        }

        setCampaign(campaignDetails);
      } catch (err: any) {
        setError(err.message || "Failed to load campaign data.");
      } finally {
        setIsLoading(false);
      }
    } else if (!auth?.isLoading) {
      setError("Authentication required.");
      setIsLoading(false);
    }
  }, [auth?.token, auth?.user?.id, auth?.isLoading, campaignId]);

  useEffect(() => {
    if (!auth?.isLoading) {
        loadCampaignData();
    }
  }, [auth?.isLoading, loadCampaignData]);

  // --- NEW: Handler for leaving the campaign ---
  const handleLeaveCampaign = async () => {
    if (!auth?.token || !campaign) return;
    
    // Find the user's own membership record to get its ID
    const myMembership = campaign.members.find(m => m.user_id === auth.user?.id && m.status === 'active');
    if (!myMembership) {
        setError("Could not find your active membership in this campaign.");
        return;
    }

    if (window.confirm(`Are you sure you want to leave the campaign "${campaign.title}"?`)) {
        setIsLeaving(true);
        setError(null);
        try {
            await campaignService.leaveCampaign(auth.token, myMembership.id);
            alert("You have left the campaign.");
            navigate('/dashboard'); // Redirect to dashboard
        } catch (err: any) {
            console.error("Failed to leave campaign:", err);
            setError(err.message || "An error occurred while trying to leave the campaign.");
        } finally {
            setIsLeaving(false);
        }
    }
  };
  // --- END NEW ---

  if (isLoading) {
    return <div className={styles.pageContainer}><p>Loading Campaign...</p></div>;
  }
  if (error) {
    return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p><Link to="/dashboard">Back to Dashboard</Link></div>;
  }
  if (!campaign) {
    return <div className={styles.pageContainer}><p>Campaign not found.</p></div>;
  }

  const activeMembers = campaign.members.filter(m => m.status.toLowerCase() === 'active');
  const isCurrentUserMember = activeMembers.some(m => m.user_id === auth.user?.id);

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.title}>{campaign.title}</h1>
        <p className={styles.dmInfo}>A Chronicle hosted by {campaign.dm?.username || 'an unknown Scribe'}</p>
      </header>

      <main className={styles.mainGrid}>
        <section className={styles.mainContent}>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Campaign Details</h2>
            {campaign.description ? (
              <p className={styles.description}>{campaign.description}</p>
            ) : (
              <p>No description provided.</p>
            )}
          </div>
          {campaign.house_rules && (
            <div className={styles.sectionBox}>
              <h2 className={styles.sectionTitle}>House Rules</h2>
              <p className={styles.description}>{campaign.house_rules}</p>
            </div>
          )}
        </section>

        <aside className={styles.sidebar}>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Adventuring Party</h2>
            <ul className={styles.memberList}>
              {activeMembers.map(member => (
                <li key={member.id} className={styles.memberItem}>
                  <span className={styles.memberName}>{member.user?.username || 'A player'}</span>
                  {member.character ? (
                    <span className={styles.memberCharacter}>
                      as {member.character.name} (Lvl {member.character.level} {member.character.race} {member.character.character_class})
                    </span>
                  ) : (
                    <span className={styles.memberCharacter}>Character not yet assigned</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
          
          {/* --- NEW: Leave Campaign Button --- */}
          {isCurrentUserMember && (
            <div className={styles.sectionBox} style={{marginTop: '1rem', textAlign: 'center'}}>
                <ThemedButton 
                    variant="red" 
                    runeSymbol="🚪"
                    onClick={handleLeaveCampaign}
                    disabled={isLeaving}
                    tooltipText="Leave this campaign permanently"
                >
                    {isLeaving ? 'Leaving...' : 'Leave Campaign'}
                </ThemedButton>
            </div>
          )}
          {/* --- END NEW --- */}
        </aside>
      </main>
    </div>
  );
};

export default CampaignViewPage;
