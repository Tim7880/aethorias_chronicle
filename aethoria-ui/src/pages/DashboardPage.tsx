// Path: src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import { campaignService } from '../services/campaignService';
import type { Character } from '../types/character';
import type { Campaign } from '../types/campaign';
import { Link, useNavigate }
from 'react-router-dom'; // useNavigate might be used for create actions
import ThemedButton from '../components/common/ThemedButton';

const DashboardPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate(); // For navigation from Create buttons

  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoadingChars, setIsLoadingChars] = useState<boolean>(true);
  const [charError, setCharError] = useState<string | null>(null);

  const [dmCampaigns, setDmCampaigns] = useState<Campaign[]>([]);
  const [isLoadingDmCampaigns, setIsLoadingDmCampaigns] = useState<boolean>(true);
  const [dmCampaignError, setDmCampaignError] = useState<string | null>(null);

  const [playerCampaigns, setPlayerCampaigns] = useState<Campaign[]>([]);
  const [isLoadingPlayerCampaigns, setIsLoadingPlayerCampaigns] = useState<boolean>(true);
  const [playerCampaignError, setPlayerCampaignError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (auth?.token && auth?.isAuthenticated) {
        setIsLoadingChars(true);
        setCharError(null);
        try {
          const userCharacters = await characterService.getCharacters(auth.token);
          setCharacters(userCharacters);
        } catch (err: any) {
          setCharError(err.message || "Could not load your characters.");
        } finally {
          setIsLoadingChars(false);
        }

        setIsLoadingDmCampaigns(true);
        setDmCampaignError(null);
        try {
          const userDmCampaigns = await campaignService.getCampaigns(auth.token, true);
          setDmCampaigns(userDmCampaigns);
        } catch (err: any) {
          setDmCampaignError(err.message || "Could not load your DM campaigns.");
        } finally {
          setIsLoadingDmCampaigns(false);
        }

        setIsLoadingPlayerCampaigns(true);
        setPlayerCampaignError(null);
        try {
          const userPlayerCampaigns = await campaignService.getCampaigns(auth.token, false);
          setPlayerCampaigns(userPlayerCampaigns);
        } catch (err: any) {
          setPlayerCampaignError(err.message || "Could not load campaigns you are in.");
        } finally {
          setIsLoadingPlayerCampaigns(false);
        }
      } else if (!auth?.isLoading) {
        setIsLoadingChars(false);
        setIsLoadingDmCampaigns(false);
        setIsLoadingPlayerCampaigns(false);
      }
    };

    fetchData();
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]); 

  // Helper function to determine the next level-up path
  const getLevelUpPath = (character: Character): string | null => {
    if (!character.level_up_status) return null;
    switch (character.level_up_status) {
      case "pending_hp":
        return `/character/${character.id}/level-up/hp`;
      case "pending_expertise": // Assuming Rogue expertise selection
        return `/character/${character.id}/level-up/expertise`; // We'll create this route next
      case "pending_archetype_selection": // Assuming Rogue archetype selection
        return `/character/${character.id}/level-up/archetype`; // We'll create this route next
      case "pending_asi":
        return `/character/${character.id}/level-up/asi`;
      case "pending_spells": // Assuming Sorcerer spell selection
        return `/character/${character.id}/level-up/spells`;
      // Add cases for other pending states like "pending_features"
      default:
        return null;
    }
  };

  const pageStyle: React.CSSProperties = { padding: '20px', fontFamily: 'var(--font-body-primary)', };
  const sectionTitleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', fontSize: '2.5em', borderBottom: '1px solid var(--ink-color-light)', paddingBottom: '0.3em', marginBottom: '1em', };
  const listStyle: React.CSSProperties = { listStyle: 'none', padding: 0, };
  const listItemStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', border: '1px solid var(--ink-color-light)', borderRadius: '5px', padding: '15px', marginBottom: '10px', boxShadow: '0px 3px 10px rgba(0,0,0,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' };
  const characterInfoStyle: React.CSSProperties = { flexGrow: 1 };
  const levelUpLinkStyle: React.CSSProperties = { 
      fontFamily: 'var(--font-script-annotation)', 
      marginLeft: '20px', 
      padding: '5px 10px',
      backgroundColor: 'var(--ink-color-medium)', // A contrasting color
      color: 'var(--parchment-bg)',
      borderRadius: '4px',
      textDecoration: 'none',
      fontSize: '0.9em',
      boxShadow: '1px 1px 3px rgba(0,0,0,0.2)'
  };


  if (auth?.isLoading) {
    return <div style={pageStyle}><p>Loading dashboard...</p></div>;
  }
  if (!auth?.isAuthenticated) {
      return ( <div style={{...pageStyle, textAlign: 'center'}}><p>Please <Link to="/login">log in</Link> to view your dashboard.</p></div>);
  }

  return (
    <div style={pageStyle}>
      <h1 style={sectionTitleStyle}>Welcome, {auth?.user?.username || 'Scribe'}!</h1>

      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Characters</h2>
        {isLoadingChars && <p>Loading characters...</p>}
        {charError && <p style={{ color: 'red' }}>Error: {charError}</p>}
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
                      {/* Later, this Link will go to /characters/{char.id} actual sheet */}
                      <Link to={`/characters/${char.id}/view`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                        {char.name}
                      </Link>
                    </h3>
                    <p style={{margin: '2px 0', fontSize: '0.9em'}}>
                      Level {char.level} {char.race} {char.character_class}
                      {char.level_up_status && ` (Status: ${char.level_up_status})`}
                    </p>
                  </div>
                  {levelUpPath && (
                    <Link to={levelUpPath} style={levelUpLinkStyle}>
                      LEVEL UP! ⬆️
                    </Link>
                  )}
                </li>
              );
            })}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            <ThemedButton 
                variant="green" 
                runeSymbol="+"
                onClick={() => navigate('/create-character')}
                tooltipText="Chronicle a new adventurer"
            >
                Create New Character
            </ThemedButton>
        </div>
      </div>

      {/* Campaigns You DM Section */}
      {/* ... (existing DM Campaigns section) ... */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You DM</h2>
        {isLoadingDmCampaigns && <p>Loading your campaigns...</p>}
        {dmCampaignError && <p style={{ color: 'red' }}>Error: {dmCampaignError}</p>}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length === 0 && ( <p>You are not currently running any campaigns.</p> )}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length > 0 && (
          <ul style={listStyle}>
            {dmCampaigns.map((camp) => (
              <li key={camp.id} style={listItemStyle}>
                <div>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                    <Link to={`/campaigns/${camp.id}/manage`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                        {camp.title}
                    </Link>
                    </h3>
                    <p style={{margin: '5px 0', fontSize: '0.9em'}}>Status: {camp.is_open_for_recruitment ? "Open for Recruitment" : "Closed"}</p>
                    <p style={{margin: '5px 0', fontSize: '0.9em'}}>{camp.members?.length || 0} member(s)</p>
                </div>
                {/* Add DM specific actions here later if needed */}
              </li>
            ))}
          </ul>
        )}
         <div style={{marginTop: '20px'}}>
            <ThemedButton variant="red" runeSymbol="📜" onClick={() => navigate('/create-campaign')}>Forge New Campaign</ThemedButton>
        </div>
      </div>


      {/* Campaigns You're In Section */}
      {/* ... (existing Player Campaigns section) ... */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You're In</h2>
        {isLoadingPlayerCampaigns && <p>Loading your active campaigns...</p>}
        {playerCampaignError && <p style={{ color: 'red' }}>Error: {playerCampaignError}</p>}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length === 0 && ( <p>You have not yet joined any campaigns as a player.</p> )}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length > 0 && (
          <ul style={listStyle}>
            {playerCampaigns.map((camp) => (
              <li key={camp.id} style={listItemStyle}>
                <div>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                       <Link to={`/campaigns/${camp.id}/play`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                        {camp.title}
                      </Link>
                    </h3>
                    <p style={{margin: '5px 0', fontSize: '0.9em'}}>DM: {camp.dm?.username || 'Unknown'}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            <ThemedButton variant="green" runeSymbol="🗺️" onClick={() => navigate('/discover-campaigns')}>Discover Campaigns</ThemedButton>
        </div>
      </div>

    </div>
  );
};

export default DashboardPage;

