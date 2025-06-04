// Path: src/pages/DiscoverCampaignsPage.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom'; // useNavigate was correctly removed as unused
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import { characterService } from '../services/characterService';
import type { Campaign, PlayerCampaignJoinRequest } from '../types/campaign';
import type { Character } from '../types/character';
import ThemedButton from '../components/common/ThemedButton';
import styles from './DiscoverCampaignsPage.module.css'; 

const DiscoverCampaignsPage: React.FC = () => {
  const auth = useAuth();
  const [discoverableCampaigns, setDiscoverableCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true); // General page loading
  const [error, setError] = useState<string | null>(null);
  const [requestStatus, setRequestStatus] = useState<Record<number, string>>({});

  const [isCharacterModalOpen, setIsCharacterModalOpen] = useState(false);
  const [selectedCampaignForJoin, setSelectedCampaignForJoin] = useState<Campaign | null>(null);
  const [ownedCharacters, setOwnedCharacters] = useState<Character[]>([]);
  const [isLoadingOwnedChars, setIsLoadingOwnedChars] = useState(false); // For modal character list
  const [characterToJoinWithId, setCharacterToJoinWithId] = useState<number | null | string>('');

  const fetchPageData = useCallback(async () => {
    if (auth?.token && auth.isAuthenticated) {
      setIsLoading(true); // For the whole page initial load
      setIsLoadingOwnedChars(true); // Also set this for initial character fetch
      setError(null);
      try {
        const campaignsData = await campaignService.getDiscoverableCampaigns(auth.token);
        setDiscoverableCampaigns(campaignsData);
        
        const userCharactersData = await characterService.getCharacters(auth.token);
        setOwnedCharacters(userCharactersData);

      } catch (err: any) {
        setError(err.message || "Could not load page data.");
      } finally {
        setIsLoading(false);
        setIsLoadingOwnedChars(false); // Ensure this is set to false
      }
    } else if (!auth?.isLoading) {
      setError("You must be logged in to discover campaigns or select characters.");
      setIsLoading(false);
      setIsLoadingOwnedChars(false);
    }
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]);

  useEffect(() => {
    if (!auth?.isLoading) {
        fetchPageData();
    }
  }, [auth?.isLoading, fetchPageData]);


  const openCharacterSelectionModal = (campaign: Campaign) => {
    setSelectedCampaignForJoin(campaign);
    setCharacterToJoinWithId(''); 
    setIsCharacterModalOpen(true);
    // Fetch characters again if modal opens, in case list changed, or rely on initial fetch
    // For simplicity, relying on initial fetch from fetchPageData
    // If characters were fetched in a separate useEffect, you might call setIsLoadingOwnedChars(true) here
  };

  const handleConfirmJoinRequest = async () => {
    if (!auth?.token || !selectedCampaignForJoin) {
      setError("Authentication or campaign selection missing.");
      return;
    }
    const campaignId = selectedCampaignForJoin.id;
    // Set status for the specific button in the main list
    setRequestStatus(prev => ({ ...prev, [campaignId]: "Requesting..." }));
    setIsCharacterModalOpen(false); 

    const payload: PlayerCampaignJoinRequest = {
      character_id: characterToJoinWithId === '' || characterToJoinWithId === null ? null : Number(characterToJoinWithId)
    };

    try {
      await campaignService.requestToJoinCampaign(auth.token, campaignId, payload);
      setRequestStatus(prev => ({ ...prev, [campaignId]: "Requested!" }));
      alert(`Your request to join "${selectedCampaignForJoin.title}" ${payload.character_id ? 'with your selected character' : 'without a character'} has been sent!`);
    } catch (err: any) {
      console.error(`Failed to request join for campaign ${campaignId}:`, err);
      setRequestStatus(prev => ({ ...prev, [campaignId]: `Error: ${err.message || 'Failed'}` }));
    }
  };
  
  if (isLoading && !discoverableCampaigns.length && !error) { 
    return <div className={styles.pageStyle}><p>Searching for open campaigns...</p></div>;
  }
  if (!auth?.isAuthenticated && !auth?.isLoading) {
    return (<div className={styles.pageStyle} style={{textAlign: 'center'}}><p>Please <Link to="/login" style={{color: 'var(--ink-color-dark)'}}>log in</Link> to discover campaigns.</p></div>);
  }
  if (error && !discoverableCampaigns.length) {
    return <div className={styles.pageStyle}><p className={styles.errorText}>{error}</p></div>;
  }

  return (
    <div className={styles.pageStyle}>
      <div className={styles.sheetContainerWithWavyEffect}> 
        <div className={styles.sheetContent}>
            <h1 className={styles.title}>Discover Open Campaigns</h1>

            {isLoading && discoverableCampaigns.length > 0 && <p className={styles.infoText}>Refreshing campaign list...</p>}
            {!isLoading && discoverableCampaigns.length === 0 && !error && (
              <p className={styles.infoText}> No campaigns are currently open for recruitment. Check back soon!</p>
            )}
            {error && <p className={styles.errorText}>{error}</p>} {/* Display general errors */}

            {discoverableCampaigns.length > 0 && (
            <ul className={styles.campaignList}>
                {discoverableCampaigns.map((campaign) => {
                  const currentRequestStatus = requestStatus[campaign.id];
                  const isButtonDisabled = !!currentRequestStatus && (currentRequestStatus === "Requesting..." || currentRequestStatus === "Requested!");
                  
                  let buttonText = "Request to Join";
                  if (currentRequestStatus) {
                    buttonText = currentRequestStatus.split(":")[0]; // Show "Requesting", "Requested", or "Error"
                  }

                  let tooltip = "Request to Join";
                  if (currentRequestStatus === "Requested!") {
                    tooltip = "Request Sent (Pending Approval)";
                  } else if (currentRequestStatus?.startsWith("Error:")) {
                    tooltip = currentRequestStatus;
                  }

                  return (
                    <li key={campaign.id} className={styles.campaignItem}>
                        <h2 className={styles.campaignTitle}>{campaign.title}</h2>
                        <p className={styles.campaignDetail}><strong>DM:</strong> {campaign.dm?.username || 'Unknown Scribe'}</p>
                        {campaign.description && (<p className={styles.campaignDescription}>{campaign.description}</p>)}
                        <p className={styles.campaignDetail}>
                        <strong>Max Players:</strong> {campaign.max_players || 'Not specified'} | 
                        <strong> Current Members:</strong> {campaign.members?.length || 0}
                        </p>
                        {campaign.next_session_utc && (<p className={styles.campaignDetail}><strong>Next Session:</strong> {new Date(campaign.next_session_utc).toLocaleString()}</p>)}
                        
                        <div className={styles.buttonContainer}>
                        <ThemedButton
                            onClick={() => openCharacterSelectionModal(campaign)}
                            disabled={isButtonDisabled}
                            variant={currentRequestStatus === "Requested!" ? undefined : "green"}
                            runeSymbol={currentRequestStatus === "Requested!" ? "⏳" : "➕"}
                            tooltipText={tooltip}
                        >
                            {buttonText}
                        </ThemedButton>
                        </div>
                    </li>
                  );
                })}
            </ul>
            )}
        </div>
      </div>

      {isCharacterModalOpen && selectedCampaignForJoin && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h2 className={styles.modalTitle}>Join Campaign: {selectedCampaignForJoin.title}</h2>
            <p className={styles.modalInfo}>Select a character to join with, or join without assigning one now.</p>
            
            {isLoadingOwnedChars && <p>Loading your characters...</p>}
            {!isLoadingOwnedChars && ownedCharacters.length === 0 && (
                <p className={styles.modalInfo}>You have no characters available. You can join without one for now.</p>
            )}
            {!isLoadingOwnedChars && ownedCharacters.length > 0 && (
                <div className={styles.modalSelectGroup}>
                    <label htmlFor="characterSelect" className={styles.modalSelectLabel}>Choose Character:</label>
                    <select 
                        id="characterSelect" 
                        value={characterToJoinWithId || ''} 
                        onChange={(e) => setCharacterToJoinWithId(e.target.value ? Number(e.target.value) : null)}
                        className={styles.modalSelectElement}
                    >
                        <option value="">Join without assigning character</option>
                        {ownedCharacters.map(char => (
                            <option key={char.id} value={char.id}>
                                {char.name} (Lvl {char.level} {char.race} {char.character_class})
                            </option>
                        ))}
                    </select>
                </div>
            )}

            <div className={styles.modalActions}>
              <ThemedButton onClick={() => setIsCharacterModalOpen(false)} variant="red" runeSymbol="✖">
                Cancel
              </ThemedButton>
              <ThemedButton onClick={handleConfirmJoinRequest} variant="green" runeSymbol="✔">
                Confirm Join Request
              </ThemedButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiscoverCampaignsPage;

