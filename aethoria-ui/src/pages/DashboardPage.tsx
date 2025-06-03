// Path: src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import { campaignService } from '../services/campaignService';
import type { Character } from '../types/character';
import type { Campaign } from '../types/campaign';
import { Link, useNavigate } from 'react-router-dom';
import ThemedButton from '../components/common/ThemedButton'; // Ensure this import is correct for your project
import stylesFromSheet from './CharacterSheetPage.module.css'; // Using styles from CharacterSheetPage for consistency

const DashboardPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate(); 

  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoadingChars, setIsLoadingChars] = useState<boolean>(true);
  const [charError, setCharError] = useState<string | null>(null);
  const [generalError, setGeneralError] = useState<string | null>(null); // For errors like delete

  const [dmCampaigns, setDmCampaigns] = useState<Campaign[]>([]);
  const [isLoadingDmCampaigns, setIsLoadingDmCampaigns] = useState<boolean>(true);
  const [dmCampaignError, setDmCampaignError] = useState<string | null>(null);

  const [playerCampaigns, setPlayerCampaigns] = useState<Campaign[]>([]);
  const [isLoadingPlayerCampaigns, setIsLoadingPlayerCampaigns] = useState<boolean>(true);
  const [playerCampaignError, setPlayerCampaignError] = useState<string | null>(null);

  const fetchData = async () => { // Combined fetchData function
    if (auth?.token && auth?.isAuthenticated) {
      setIsLoadingChars(true); setCharError(null);
      setIsLoadingDmCampaigns(true); setDmCampaignError(null);
      setIsLoadingPlayerCampaigns(true); setPlayerCampaignError(null);
      setGeneralError(null);

      try {
        // Use Promise.all to fetch all data concurrently
        const [userCharacters, userDmCampaigns, userPlayerCampaigns] = await Promise.all([
          characterService.getCharacters(auth.token),
          campaignService.getCampaigns(auth.token, true), // as DM
          campaignService.getCampaigns(auth.token, false) // as Player
        ]);
        setCharacters(userCharacters);
        setDmCampaigns(userDmCampaigns);
        setPlayerCampaigns(userPlayerCampaigns);
      } catch (err: any) {
        console.error("Failed to fetch dashboard data:", err);
        setGeneralError(err.message || "Could not load all dashboard data. Some sections might be incomplete.");
        // Individual error states will also be set if Promise.all is not used or for more granular errors
      } finally {
        setIsLoadingChars(false);
        setIsLoadingDmCampaigns(false);
        setIsLoadingPlayerCampaigns(false);
      }
    } else if (!auth?.isLoading) { // Only if auth is not in its initial loading phase
      // Clear data if not authenticated or token is missing
      setCharacters([]);
      setDmCampaigns([]);
      setPlayerCampaigns([]);
      setIsLoadingChars(false);
      setIsLoadingDmCampaigns(false);
      setIsLoadingPlayerCampaigns(false);
    }
  };

  useEffect(() => {
    if (!auth?.isLoading) { 
        fetchData();
    }
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]); 

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

  // --- NEW: Delete Character Handler ---
  const handleDeleteCharacter = async (characterId: number, characterName: string) => {
    if (!auth?.token) {
      setGeneralError("Authentication required to delete characters.");
      return;
    }
    if (window.confirm(`Are you sure you want to permanently delete "${characterName}"? This action cannot be undone.`)) {
      setGeneralError(null); // Clear previous general errors
      try {
        await characterService.deleteCharacter(auth.token, characterId);
        // Refresh character list by removing the deleted character from state
        setCharacters(prevChars => prevChars.filter(char => char.id !== characterId));
        alert(`"${characterName}" has been deleted successfully.`);
      } catch (err: any) {
        console.error("Failed to delete character:", err);
        setGeneralError(err.message || `Could not delete "${characterName}".`);
      }
    }
  };
  // --- END NEW ---

  const pageStyle: React.CSSProperties = { padding: '20px', fontFamily: 'var(--font-body-primary)', };
  const sectionTitleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', fontSize: '2.5em', borderBottom: '1px solid var(--ink-color-light)', paddingBottom: '0.3em', marginBottom: '1em', };
  const listStyle: React.CSSProperties = { listStyle: 'none', padding: 0, };
  const listItemStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', border: '1px solid var(--ink-color-light)', borderRadius: '5px', padding: '15px', marginBottom: '10px', boxShadow: '0px 3px 10px rgba(0,0,0,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
  const characterInfoStyle: React.CSSProperties = { flexGrow: 1, marginRight: '10px' }; // Added marginRight
  const levelUpLinkStyle: React.CSSProperties = { fontFamily: 'var(--font-script-annotation)', padding: '6px 12px', backgroundColor: 'var(--ink-color-medium)', color: 'var(--parchment-bg)', borderRadius: '4px', textDecoration: 'none', fontSize: '1em', boxShadow: '1px 1px 3px rgba(0,0,0,0.2)', whiteSpace: 'nowrap'};
  const actionsContainerStyle: React.CSSProperties = { // For Level Up and Delete buttons
    display: 'flex',
    alignItems: 'center',
    gap: '10px' 
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
      
      {/* Characters Section */}
      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Characters</h2>
        {(isLoadingChars && !characters.length && !charError) && <p>Loading characters...</p>}
        {charError && <p className={stylesFromSheet.errorText}>{charError}</p>}
        {!isLoadingChars && !charError && characters.length === 0 && (
          <p>You have not yet chronicled any adventurers.</p>
        )}
        {!isLoadingChars && !charError && characters.length > 0 && (
          <ul style={listStyle}>
            {characters.map((char) => {
              const levelUpPath = getLevelUpPath(char);
              return (
                <li key={char.id} style={listItemStyle}>
                  <div style={characterInfoStyle}>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 5px 0'}}>
                      <Link to={`/characters/${char.id}/view`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                        {char.name}
                      </Link>
                    </h3>
                    <p style={{margin: '2px 0', fontSize: '0.9em'}}>
                      Level {char.level} {char.race} {char.character_class}
                      {char.level_up_status && ` (Status: ${char.level_up_status.replace('pending_', '')})`}
                    </p>
                  </div>
                  <div style={actionsContainerStyle}>
                    {levelUpPath && (
                      <Link to={levelUpPath} style={levelUpLinkStyle}>
                        LEVEL UP! ⬆️
                      </Link>
                    )}
                    <ThemedButton
                      onClick={() => handleDeleteCharacter(char.id, char.name)}
                      variant="red"
                      runeSymbol="🗑️"
                      tooltipText={`Delete ${char.name}`}
                      style={{padding: '4px 8px', fontSize: '0.8em', minWidth: '30px', minHeight: '30px', lineHeight: 'initial'}}
                      aria-label={`Delete ${char.name}`}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            <ThemedButton variant="green" runeSymbol="+" onClick={() => navigate('/create-character')} tooltipText="Chronicle a new adventurer">
                Create New Character
            </ThemedButton>
        </div>
      </div>

      {/* Campaigns You DM Section */}
      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You DM</h2>
        {(isLoadingDmCampaigns && !dmCampaigns.length && !dmCampaignError) && <p>Loading your campaigns...</p>}
        {dmCampaignError && <p className={stylesFromSheet.errorText}>{dmCampaignError}</p>}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length === 0 && ( <p>You are not currently running any campaigns.</p> )}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length > 0 && ( <ul style={listStyle}> {dmCampaigns.map(camp => ( <li key={camp.id} style={listItemStyle}> <div> <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}> <Link to={`/campaigns/${camp.id}/manage`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}> {camp.title} </Link> </h3> <p style={{margin: '5px 0', fontSize: '0.9em'}}>Status: {camp.is_open_for_recruitment ? "Open" : "Closed"}</p> <p style={{margin: '5px 0', fontSize: '0.9em'}}>{camp.members?.length || 0} member(s)</p> </div> </li> ))} </ul> )}
         <div style={{marginTop: '20px'}}>
            <ThemedButton variant="red" runeSymbol="📜" onClick={() => navigate('/create-campaign')}>Forge New Campaign</ThemedButton>
        </div>
      </div>

      {/* Campaigns You're In Section */}
      <div className={stylesFromSheet.box} style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You're In</h2>
        {(isLoadingPlayerCampaigns && !playerCampaigns.length && !playerCampaignError) && <p>Loading your active campaigns...</p>}
        {playerCampaignError && <p className={stylesFromSheet.errorText}>{playerCampaignError}</p>}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length === 0 && ( <p>You have not yet joined any campaigns as a player.</p> )}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length > 0 && ( <ul style={listStyle}> {playerCampaigns.map(camp => ( <li key={camp.id} style={listItemStyle}> <div> <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}> <Link to={`/campaigns/${camp.id}/play`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}> {camp.title} </Link> </h3> <p style={{margin: '5px 0', fontSize: '0.9em'}}>DM: {camp.dm?.username || 'Unknown'}</p> </div> </li> ))} </ul> )}
        <div style={{marginTop: '20px'}}>
            <ThemedButton variant="green" runeSymbol="🗺️" onClick={() => navigate('/discover-campaigns')}>Discover Campaigns</ThemedButton>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;