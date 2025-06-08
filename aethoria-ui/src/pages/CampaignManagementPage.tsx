// Path: src/pages/CampaignManagementPage.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { XpAwardPayload } from '../services/campaignService';
import type { Campaign, CampaignMember } from '../types/campaign';
import ThemedButton from '../components/common/ThemedButton';
import ThemedInput from '../components/common/ThemedInput';
import styles from './CampaignManagementPage.module.css'; 

const CampaignManagementPage: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const auth = useAuth();
  const navigate = useNavigate();

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [joinRequests, setJoinRequests] = useState<CampaignMember[]>([]);
  const [activeMembers, setActiveMembers] = useState<CampaignMember[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  const [error, setError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<Record<number, string>>({});
  const [xpAmount, setXpAmount] = useState('');
  const [xpTargetMode, setXpTargetMode] = useState<'all' | 'select'>('all');
  const [selectedCharIdsForXp, setSelectedCharIdsForXp] = useState<number[]>([]);
  const [xpAwardError, setXpAwardError] = useState<string | null>(null);
  const [isAwardingXp, setIsAwardingXp] = useState(false);
  const [xpAwardSuccess, setXpAwardSuccess] = useState<string | null>(null);

  const loadCampaignData = useCallback(async () => {
    if (auth?.token && campaignId) {
      setIsLoading(true); // Always set main loading on a full fetch
      setError(null);
      setActionStatus({}); // Reset all button statuses on every data refresh
      
      try {
        const id = parseInt(campaignId, 10);
        if (isNaN(id)) throw new Error("Invalid campaign ID in URL.");
        
        const [campaignDetails, pendingRequestsData, activeMembersData] = await Promise.all([
            campaignService.getCampaignById(auth.token, id),
            campaignService.getCampaignJoinRequests(auth.token, id),
            campaignService.getActiveCampaignMembers(auth.token, id)
        ]);

        setCampaign(campaignDetails);
        setJoinRequests(pendingRequestsData.filter(req => req.status === "pending_approval"));
        setActiveMembers(activeMembersData.filter(mem => mem.user_id !== campaignDetails.dm_user_id));

        if (campaignDetails && campaignDetails.dm_user_id !== auth.user?.id) {
          setError("You are not authorized to manage this campaign.");
          setTimeout(() => navigate('/dashboard'), 3000);
          return; 
        }
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
      alert("Join request approved!");
      loadCampaignData(); // Re-fetch all data to update both lists
    } catch (err: any) {
      console.error("Approval error:", err);
      const errorMessage = err.message || 'Failed to approve request.';
      setActionStatus(prev => ({ ...prev, [requesterUserId]: `Error`})); // Simplified error status
      setError(errorMessage); 
    }
  };

  const handleRejectRequest = async (requesterUserId: number) => {
    if (!auth?.token || !campaignId) return;
    const campaignIdNum = parseInt(campaignId, 10);
    setActionStatus(prev => ({ ...prev, [requesterUserId]: "Rejecting..."}));
    try {
      await campaignService.rejectJoinRequest(auth.token, campaignIdNum, requesterUserId);
      alert("Join request rejected.");
      setJoinRequests(prev => prev.filter(req => req.user?.id !== requesterUserId));
    } catch (err: any) {
      console.error("Rejection error:", err);
      const errorMessage = err.message || 'Failed to reject request.';
      setActionStatus(prev => ({ ...prev, [requesterUserId]: `Error`}));
      setError(errorMessage);
    }
  };

  const handleRemoveMember = async (memberUserId: number, memberUsername: string) => {
    if (!auth?.token || !campaignId) return;
    if (window.confirm(`Are you sure you want to remove ${memberUsername} from the campaign?`)) {
        const campaignIdNum = parseInt(campaignId, 10);
        setActionStatus(prev => ({...prev, [memberUserId]: "Removing..."}));
        try {
            await campaignService.removeMemberByDM(auth.token, campaignIdNum, memberUserId);
            alert(`${memberUsername} has been removed from the campaign.`);
            loadCampaignData(); 
        } catch (err: any) {
            console.error("Failed to remove member:", err);
            setActionStatus(prev => ({...prev, [memberUserId]: `Error`}));
            setError(err.message || "Could not remove member.");
        }
    }
  };

  const handleXpCharacterSelection = (characterId: number) => {
    setSelectedCharIdsForXp(prev => 
        prev.includes(characterId) 
            ? prev.filter(id => id !== characterId) 
            : [...prev, characterId]
    );
  };

  const handleAwardXp = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!auth?.token || !campaignId) return;

    setXpAwardError(null);
    setXpAwardSuccess(null);
    setIsAwardingXp(true);

    const amount = parseInt(xpAmount, 10);
    if (isNaN(amount) || amount <= 0) {
        setXpAwardError("Please enter a valid, positive XP amount.");
        setIsAwardingXp(false);
        return;
    }

    let character_ids: number[] = [];
    if (xpTargetMode === 'all') {
        character_ids = activeMembers
            .filter(m => m.character?.id)
            .map(m => m.character!.id);
    } else {
        character_ids = selectedCharIdsForXp;
    }

    if (character_ids.length === 0) {
        setXpAwardError("Please select at least one character to award XP.");
        setIsAwardingXp(false);
        return;
    }

    const payload: XpAwardPayload = { amount, character_ids };
    
    try {
        await campaignService.awardXpToCharacters(auth.token, parseInt(campaignId, 10), payload);
        setXpAwardSuccess(`${amount} XP awarded successfully! Players' characters have been updated.`);
        setXpAmount('');
        setSelectedCharIdsForXp([]);
        setTimeout(() => {
            setXpAwardSuccess(null);
            loadCampaignData(); 
        }, 3000);

    } catch (err: any) {
        setXpAwardError(err.message || "Failed to award XP.");
    } finally {
        setIsAwardingXp(false);
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
  if (campaign.dm_user_id !== auth?.user?.id) {
     return <div className={styles.pageStyle}><p className={styles.errorText}>You are not authorized to manage this campaign.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
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
                  <li key={`request-${request.id}`} className={styles.requestItem}>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.6em', margin: '0 0 10px 0'}}>
                      Request from: {request.user?.username || 'Unknown User'}
                    </h3>
                    {request.character && (
                      <div className={styles.requestCharacterInfo}>
                        <p><strong>Character:</strong> {request.character.name}</p>
                        <p>Lvl {request.character.level} {request.character.race} {request.character.character_class}</p>
                        <p>Alignment: {request.character.alignment || 'N/A'}</p>
                      </div>
                    )}
                    {!request.character && <p className={styles.requestCharacterInfo}>No character specified for this request.</p>}
                    <div className={styles.requestActions}>
                      <ThemedButton
                        onClick={() => handleApproveRequest(request.user_id)}
                        disabled={!!actionStatus[request.user_id]}
                        variant="green" runeSymbol="✔" tooltipText="Approve Request"
                        style={{fontSize: '0.9em', padding: '6px 12px'}}
                      >
                        {actionStatus[request.user_id] || "Approve"}
                      </ThemedButton>
                      <ThemedButton
                        onClick={() => handleRejectRequest(request.user_id)}
                        disabled={!!actionStatus[request.user_id]}
                        variant="red" runeSymbol="✖" tooltipText="Reject Request"
                        style={{fontSize: '0.9em', padding: '6px 12px'}}
                      >
                         {actionStatus[request.user_id] || "Reject"}
                      </ThemedButton>
                    </div>
                     {actionStatus[request.user_id]?.startsWith("Error:") && (
                        <p className={styles.errorText} style={{fontSize: '0.8em', marginTop: '5px', textAlign:'right'}}>{actionStatus[request.user_id]}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className={styles.box} style={{marginTop: '30px'}}>
            <h2 className={styles.sectionTitle}>Active Members ({activeMembers.length} / {campaign.max_players || 'Unlimited'})</h2>
            {isLoading && !activeMembers.length && <p>Loading members...</p>}
            {!isLoading && activeMembers.length === 0 && (
              <p className={styles.infoTextLeft}>No active members in this campaign yet.</p>
            )}
            {activeMembers.length > 0 && (
              <ul style={{listStyle: 'none', padding: 0}}>
                {activeMembers.map(member => (
                  <li key={`member-${member.id}`} className={styles.requestItem} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.4em', margin: '0 0 5px 0'}}>
                        {member.user?.username || 'Unknown User'}
                      </h3>
                      {member.character && (
                        <div className={styles.requestCharacterInfo} style={{paddingLeft: 0, borderLeft: 'none', fontSize: '0.9em'}}>
                          <p>Playing as: {member.character.name} (Lvl {member.character.level} {member.character.race} {member.character.character_class})</p>
                        </div>
                      )}
                      {!member.character && <p className={styles.requestCharacterInfo} style={{paddingLeft: 0, borderLeft: 'none', fontSize: '0.9em'}}>No character assigned.</p>}
                    </div>
                    <ThemedButton 
                        variant="red" 
                        runeSymbol="✖️"
                        onClick={() => handleRemoveMember(member.user_id, member.user?.username || 'this player')}
                        disabled={!!actionStatus[member.user_id]}
                        tooltipText={`Remove ${member.user?.username || 'player'} from campaign`}
                        style={{fontSize: '0.8em', padding: '6px 10px'}}
                    >
                        {actionStatus[member.user_id] || "Remove"}
                    </ThemedButton>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* --- NEW: Award Experience Section --- */}
          <div className={styles.box} style={{marginTop: '30px'}}>
            <h2 className={styles.sectionTitle}>Award Experience</h2>
            <form onSubmit={handleAwardXp} className={styles.xpAwardForm}>
              <div className={styles.xpInputContainer}>
                <ThemedInput
                  label="XP Amount to Award"
                  id="xpAmount"
                  name="xpAmount"
                  type="number"
                  value={xpAmount}
                  onChange={(e) => setXpAmount(e.target.value)}
                  min="1"
                  required
                />
              </div>

              <div className={styles.xpTargetToggle}>
                <label>
                  <input type="radio" name="xpTargetMode" value="all" checked={xpTargetMode === 'all'} onChange={(e) => setXpTargetMode(e.target.value as 'all' | 'select')} />
                  All Active Players
                </label>
                <label>
                  <input type="radio" name="xpTargetMode" value="select" checked={xpTargetMode === 'select'} onChange={(e) => setXpTargetMode(e.target.value as 'all' | 'select')} />
                  Select Players
                </label>
              </div>

              {xpTargetMode === 'select' && (
                <div className={styles.xpCharacterList}>
                  {activeMembers.filter(m => m.character).length > 0 ? activeMembers.filter(m => m.character).map(member => (
                    <div key={`xp-char-${member.character!.id}`} className={styles.xpCharacterItem}>
                      <input
                        type="checkbox"
                        id={`xp-char-checkbox-${member.character!.id}`}
                        checked={selectedCharIdsForXp.includes(member.character!.id)}
                        onChange={() => handleXpCharacterSelection(member.character!.id)}
                        className={styles.xpCheckbox}
                      />
                      <label htmlFor={`xp-char-checkbox-${member.character!.id}`} className={styles.xpCharacterLabel}>
                        {member.character!.name}
                        <div className={styles.xpCharacterDetails}>Player: {member.user?.username}</div>
                      </label>
                    </div>
                  )) : <p className={styles.infoTextLeft}>No characters assigned to active players.</p>}
                </div>
              )}
              
              {xpAwardError && <p className={styles.errorText} style={{marginTop: '1rem'}}>{xpAwardError}</p>}
              {xpAwardSuccess && <p className={styles.successText} style={{marginTop: '1rem'}}>{xpAwardSuccess}</p>}

              <div className={styles.buttonContainer}>
                <ThemedButton
                  type="submit"
                  variant="green"
                  runeSymbol="🌟"
                  tooltipText="Grant Experience Points"
                  disabled={isAwardingXp}
                >
                  {isAwardingXp ? "Granting..." : "Grant XP"}
                </ThemedButton>
              </div>
            </form>
          </div>
          {/* --- END NEW --- */}

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
