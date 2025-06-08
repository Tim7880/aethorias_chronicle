// Path: src/pages/DashboardPage.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import { campaignService } from '../services/campaignService';
import type { Character } from '../types/character';
import type { Campaign, CampaignMember } from '../types/campaign';
import { Link, useNavigate } from 'react-router-dom';
import ThemedButton from '../components/common/ThemedButton';
import stylesFromSheet from './CharacterSheetPage.module.css'; 

const DashboardPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate(); 

  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoadingChars, setIsLoadingChars] = useState<boolean>(true);
  const [charError, setCharError] = useState<string | null>(null);
  
  const [dmCampaigns, setDmCampaigns] = useState<Campaign[]>([]);
  const [isLoadingDmCampaigns, setIsLoadingDmCampaigns] = useState<boolean>(true);
  const [dmCampaignError, setDmCampaignError] = useState<string | null>(null);

  const [myCampaignMemberships, setMyCampaignMemberships] = useState<CampaignMember[]>([]);
  const [isLoadingMyMemberships, setIsLoadingMyMemberships] = useState<boolean>(true);
  const [myMembershipsError, setMyMembershipsError] = useState<string | null>(null);
  
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<Record<number, string>>({}); // For tracking cancel actions

  const fetchData = useCallback(async () => {
    if (auth?.token && auth?.isAuthenticated) {
      setIsLoadingChars(true); setCharError(null);
      setIsLoadingDmCampaigns(true); setDmCampaignError(null);
      setIsLoadingMyMemberships(true); setMyMembershipsError(null);
      setGeneralError(null);

      try {
        const [
            userCharacters, 
            userDmCampaigns, 
            userMemberships 
        ] = await Promise.all([
          characterService.getCharacters(auth.token),
          campaignService.getCampaigns(auth.token, true),
          campaignService.getMyCampaignMemberships(auth.token)
        ]);
        setCharacters(userCharacters);
        setDmCampaigns(userDmCampaigns);
        setMyCampaignMemberships(userMemberships);

      } catch (err: any) {
        console.error("Failed to fetch dashboard data:", err);
        if (!characters.length) setCharError(err.message || "Could not load characters.");
        if (!dmCampaigns.length) setDmCampaignError(err.message || "Could not load DM campaigns.");
        if (!myCampaignMemberships.length) setMyMembershipsError(err.message || "Could not load your campaign statuses.");
        setGeneralError(err.message || "Could not load all dashboard data.");
      } finally {
        setIsLoadingChars(false);
        setIsLoadingDmCampaigns(false);
        setIsLoadingMyMemberships(false);
      }
    } else if (!auth?.isLoading) {
      setCharacters([]); setDmCampaigns([]); setMyCampaignMemberships([]);
      setIsLoadingChars(false); setIsLoadingDmCampaigns(false); setIsLoadingMyMemberships(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]);

  useEffect(() => {
    if (!auth?.isLoading) { 
        fetchData();
    }
  }, [auth?.isLoading, fetchData]); // fetchData is now a stable dependency

  const getLevelUpPath = (character: Character): string | null => {
    if (!character.level_up_status) return null;
    switch (character.level_up_status) {
      case "pending_hp": return `/character/${character.id}/level-up/hp`;
      case "pending_expertise": return `/character/${character.id}/level-up/expertise`;
      case "pending_archetype_selection": return `/character/${character.id}/level-up/archetype`;
      case "pending_asi": return `/character/${character.id}/level-up/asi`;
      case "pending_spells": return `/character/${character.id}/level-up/spells`;
      default: return null;
    }
  };

  const handleDeleteCharacter = async (characterId: number, characterName: string) => {
    if (!auth?.token) {
      setGeneralError("Authentication required to delete characters."); return;
    }
    if (window.confirm(`Are you sure you want to permanently delete "${characterName}"? This action cannot be undone.`)) {
      setGeneralError(null); 
      try {
        await characterService.deleteCharacter(auth.token, characterId);
        setCharacters(prevChars => prevChars.filter(char => char.id !== characterId));
        alert(`"${characterName}" has been deleted successfully.`);
      } catch (err: any) {
        console.error("Failed to delete character:", err);
        setGeneralError(err.message || `Could not delete "${characterName}".`);
      }
    }
  };

  // --- NEW: Cancel Join Request Handler ---
  const handleCancelJoinRequest = async (campaignMemberId: number, campaignTitle: string) => {
    if (!auth?.token) {
      setGeneralError("Authentication required to cancel requests.");
      return;
    }
    if (window.confirm(`Are you sure you want to cancel your request to join "${campaignTitle}"?`)) {
      setGeneralError(null);
      setActionStatus(prev => ({...prev, [campaignMemberId]: "Canceling..."}));
      try {
        await campaignService.cancelJoinRequest(auth.token, campaignMemberId);
        setMyCampaignMemberships(prevMemberships => 
            prevMemberships.filter(m => m.id !== campaignMemberId)
        );
        alert("Your join request has been successfully canceled.");
      } catch (err: any) {
        console.error("Failed to cancel join request:", err);
        setGeneralError(err.message || "Could not cancel your request.");
        setActionStatus(prev => ({...prev, [campaignMemberId]: "Error"}));
      }
    }
  };
  // --- END NEW ---

  const pageStyle: React.CSSProperties = { padding: '20px', fontFamily: 'var(--font-body-primary)', };
  const sectionTitleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', fontSize: '2.5em', borderBottom: '1px solid var(--ink-color-light)', paddingBottom: '0.3em', marginBottom: '1em', };
  const listStyle: React.CSSProperties = { listStyle: 'none', padding: 0, };
  const listItemStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', border: '1px solid var(--ink-color-light)', borderRadius: '5px', padding: '15px', marginBottom: '10px', boxShadow: '0px 3px 10px rgba(0,0,0,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
  const characterInfoStyle: React.CSSProperties = { flexGrow: 1, marginRight: '10px' };
  const levelUpLinkStyle: React.CSSProperties = { fontFamily: 'var(--font-script-annotation)', padding: '6px 12px', backgroundColor: 'var(--ink-color-medium)', color: 'var(--parchment-bg)', borderRadius: '4px', textDecoration: 'none', fontSize: '1em', boxShadow: '1px 1px 3px rgba(0,0,0,0.2)', whiteSpace: 'nowrap'};
  const actionsContainerStyle: React.CSSProperties = { display: 'flex', alignItems: 'center', gap: '10px' };
  const statusTagStyle = (status: string): React.CSSProperties => {
    let backgroundColor = 'var(--ink-color-light)'; 
    let color = 'var(--ink-color-dark)';
    const lowerStatus = status.toLowerCase();
    if (lowerStatus === 'active') {
        backgroundColor = 'rgba(0, 128, 0, 0.2)'; 
        color = 'darkgreen';
    } else if (lowerStatus === 'rejected' || lowerStatus === 'kicked' || lowerStatus === 'left') {
        backgroundColor = 'rgba(255, 0, 0, 0.15)'; 
        color = '#a02c2c';
    } else if (lowerStatus === 'pending_approval' || lowerStatus === 'invited') {
        backgroundColor = 'rgba(255, 165, 0, 0.2)'; 
        color = '#b07400';
    }
    return {
        marginLeft: '10px', padding: '3px 8px', borderRadius: '4px',
        fontSize: '0.8em', fontWeight: 'bold', backgroundColor, color,
        border: `1px solid ${color}`
    };
  };

  if (auth?.isLoading) {
    return <div style={pageStyle}><p>Loading dashboard...</p></div>;
  }
  if (!auth?.isAuthenticated) {
      return ( <div style={{...pageStyle, textAlign: 'center'}}><p>Please <Link to="/login" style={{color: 'var(--ink-color-dark)'}}>log in</Link> to view your dashboard.</p></div>);
  }

  return (
    <div style={pageStyle}>
      <h1 style={sectionTitleStyle}>Welcome, {auth?.user?.username || 'Scribe'}!</h1>
      {generalError && <p className={stylesFromSheet.errorText} style={{textAlign: 'center', marginBottom: '15px'}}>{generalError}</p>}
      
      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Characters</h2>
        {(isLoadingChars && !characters.length && !charError) && <p>Loading characters...</p>}
        {charError && <p className={stylesFromSheet.errorText}>{charError}</p>}
        {!isLoadingChars && !charError && characters.length === 0 && ( <p>You have not yet chronicled any adventurers.</p> )}
        {!isLoadingChars && !charError && characters.length > 0 && ( <ul style={listStyle}> {characters.map((char) => { const levelUpPath = getLevelUpPath(char); return ( <li key={char.id} style={listItemStyle}> <div style={characterInfoStyle}> <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 5px 0'}}> <Link to={`/characters/${char.id}/view`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}> {char.name} </Link> </h3> <p style={{margin: '2px 0', fontSize: '0.9em'}}> Level {char.level} {char.race} {char.character_class} {char.level_up_status && ` (Status: ${char.level_up_status.replace('pending_', '')})`} </p> </div> <div style={actionsContainerStyle}> {levelUpPath && ( <Link to={levelUpPath} style={levelUpLinkStyle}> LEVEL UP! ⬆️ </Link> )} <ThemedButton onClick={() => handleDeleteCharacter(char.id, char.name)} variant="red" runeSymbol="🗑️" tooltipText={`Delete ${char.name}`} style={{padding: '4px 8px', fontSize: '0.8em', minWidth: '30px', minHeight: '30px', lineHeight: 'initial'}} aria-label={`Delete ${char.name}`} /> </div> </li> ); })} </ul> )}
        <div style={{marginTop: '20px'}}> <ThemedButton variant="green" runeSymbol="+" onClick={() => navigate('/create-character')} tooltipText="Chronicle a new adventurer"> Create New Character </ThemedButton> </div>
      </div>

      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>My Campaign Involvements</h2>
        {(isLoadingMyMemberships && !myCampaignMemberships.length && !myMembershipsError) && <p>Loading your campaign statuses...</p>}
        {myMembershipsError && <p className={stylesFromSheet.errorText}>{myMembershipsError}</p>}
        {!isLoadingMyMemberships && !myMembershipsError && myCampaignMemberships.length === 0 && (
          <p>You haven't requested to join or been added to any campaigns yet. Why not <Link to="/discover-campaigns" style={{color: "var(--ink-color-dark)"}}>discover some</Link>?</p>
        )}
        {!isLoadingMyMemberships && !myMembershipsError && myCampaignMemberships.length > 0 && (
          <ul style={listStyle}>
            {myCampaignMemberships.map((membership) => (
              <li key={`membership-${membership.id}`} style={listItemStyle}>
                <div style={characterInfoStyle}>
                  <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.6em', margin: '0 0 5px 0'}}>
                    <Link 
                        to={membership.status.toLowerCase() === 'active' ? `/campaigns/${membership.campaign_id}/play` : `/campaigns/${membership.campaign_id}/view`} 
                        style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}
                    >
                      {membership.campaign?.title || `Campaign (ID: ${membership.campaign_id})`}
                    </Link>
                    {membership.campaign?.dm?.username && (
                        <span style={{fontSize: '0.8em', color: 'var(--ink-color-medium)', marginLeft: '10px'}}>
                            (DM: {membership.campaign.dm.username})
                        </span>
                    )}
                  </h3>
                  <p style={{margin: '2px 0', fontSize: '0.9em'}}>
                    Your Status: 
                    <span style={statusTagStyle(membership.status)}>
                        {membership.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </p>
                  {membership.character && (
                     <p style={{margin: '2px 0 0 0', fontSize: '0.85em', color: 'var(--ink-color-medium)'}}>
                        Playing as: {membership.character.name} (Lvl {membership.character.level} {membership.character.race} {membership.character.character_class})
                     </p>
                  )}
                </div>
                {/* --- UPDATED: Actions Container --- */}
                <div style={actionsContainerStyle}>
                  {membership.status.toLowerCase() === 'pending_approval' && (
                    <ThemedButton 
                        onClick={() => handleCancelJoinRequest(membership.id, membership.campaign?.title || 'this campaign')}
                        variant='red' 
                        runeSymbol='✖️' 
                        tooltipText='Cancel Join Request' 
                        style={{fontSize:'0.8em', padding: '6px 10px'}}
                        disabled={!!actionStatus[membership.id]} // Disable button during action
                    >
                        {actionStatus[membership.id] || "Cancel"}
                    </ThemedButton>
                  )}
                   {membership.status.toLowerCase() === 'active' && (
                    <ThemedButton 
                        variant={undefined}
                        runeSymbol='⚔️' 
                        tooltipText='Go to Campaign' 
                        onClick={() => navigate(`/campaigns/${membership.campaign_id}/play`)} 
                        style={{fontSize:'0.9em', padding: '6px 10px'}}
                    >
                        Play
                    </ThemedButton>
                  )}
                </div>
                {/* --- END UPDATE --- */}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
         <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You DM</h2>
        {(isLoadingDmCampaigns && !dmCampaigns.length && !dmCampaignError) && <p>Loading your campaigns...</p>}
        {dmCampaignError && <p className={stylesFromSheet.errorText}>{dmCampaignError}</p>}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length === 0 && ( <p>You are not currently running any campaigns.</p> )}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length > 0 && ( <ul style={listStyle}> {dmCampaigns.map(camp => ( <li key={camp.id} style={listItemStyle}> <div style={characterInfoStyle}> <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}> <Link to={`/campaigns/${camp.id}/manage`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}> {camp.title} </Link> </h3> <p style={{margin: '5px 0', fontSize: '0.9em'}}>Status: {camp.is_open_for_recruitment ? "Open" : "Closed"}</p> <p style={{margin: '5px 0', fontSize: '0.9em'}}>{camp.members?.length || 0} member(s)</p> </div> </li> ))} </ul> )}
        <div style={{marginTop: '20px'}}> <ThemedButton variant="red" runeSymbol="📜" onClick={() => navigate('/create-campaign')}>Forge New Campaign</ThemedButton> </div>
      </div>
    </div>
  );
};

export default DashboardPage;
