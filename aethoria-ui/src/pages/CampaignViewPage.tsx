// Path: src/pages/CampaignViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { Campaign } from '../types/campaign';
import styles from './CampaignViewPage.module.css';

const CampaignViewPage: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const auth = useAuth();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCampaignData = async () => {
      if (auth?.token && campaignId) {
        setIsLoading(true);
        setError(null);
        try {
          const id = parseInt(campaignId, 10);
          if (isNaN(id)) throw new Error("Invalid campaign ID.");
          
          const campaignDetails = await campaignService.getCampaignById(auth.token, id);
          
          // Authorization Check: Must be a member or the DM to view
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
    };

    if (!auth?.isLoading) {
        loadCampaignData();
    }
  }, [auth?.token, auth?.user?.id, auth?.isLoading, campaignId]);

  if (isLoading) {
    return <div className={styles.pageContainer}><p>Loading Campaign...</p></div>;
  }

  if (error) {
    return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;
  }

  if (!campaign) {
    return <div className={styles.pageContainer}><p>Campaign not found.</p></div>;
  }

  const activeMembers = campaign.members.filter(m => m.status.toLowerCase() === 'active');

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
          {/* TODO: Add Leave Campaign Button here */}
        </aside>
      </main>
    </div>
  );
};

export default CampaignViewPage;
