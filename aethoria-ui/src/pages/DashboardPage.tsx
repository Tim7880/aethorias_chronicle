// Path: src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import { campaignService } from '../services/campaignService'; // <--- NEW IMPORT
import type { Character } from '../types/character';
import type { Campaign } from '../types/campaign'; // <--- NEW IMPORT
import { Link } from 'react-router-dom';
import ThemedButton from '../components/common/ThemedButton';

const DashboardPage: React.FC = () => {
  const auth = useAuth();

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
        // Fetch Characters
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

        // Fetch Campaigns as DM
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

        // Fetch Campaigns as Player
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

  const pageStyle: React.CSSProperties = { /* ... same as before ... */ 
      padding: '20px', fontFamily: 'var(--font-body-primary)',
  };
  const sectionTitleStyle: React.CSSProperties = { /* ... same as before ... */ 
      fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)',
      fontSize: '2.5em', borderBottom: '1px solid var(--ink-color-light)',
      paddingBottom: '0.3em', marginBottom: '1em',
  };
  const listStyle: React.CSSProperties = { /* ... same as before ... */ 
      listStyle: 'none', padding: 0,
  };
  const listItemStyle: React.CSSProperties = { /* ... same as before ... */ 
      backgroundColor: 'var(--parchment-highlight)', border: '1px solid var(--ink-color-light)',
      borderRadius: '5px', padding: '15px', marginBottom: '10px',
      boxShadow: '0px 3px 10px rgba(0,0,0,0.08)',
  };

  if (auth?.isLoading) {
    return <div style={pageStyle}><p>Loading dashboard...</p></div>;
  }

  if (!auth?.isAuthenticated) {
      return (
          <div style={{...pageStyle, textAlign: 'center'}}>
              <p>Please <Link to="/login">log in</Link> to view your dashboard.</p>
          </div>
      );
  }

  return (
    <div style={pageStyle}>
      <h1 style={sectionTitleStyle}>
        Welcome, {auth?.user?.username || 'Scribe'}!
      </h1>

      {/* Characters Section */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Characters</h2>
        {isLoadingChars && <p>Loading characters...</p>}
        {charError && <p style={{ color: 'red' }}>Error: {charError}</p>}
        {!isLoadingChars && !charError && characters.length === 0 && (
          <p>You have not yet chronicled any adventurers.</p>
        )}
        {!isLoadingChars && !charError && characters.length > 0 && (
          <ul style={listStyle}>
            {characters.map((char) => (
              <li key={char.id} style={listItemStyle}>
                <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                  <Link to={`/characters/${char.id}`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                    {char.name}
                  </Link>
                </h3>
                <p style={{margin: '5px 0'}}>Level {char.level} {char.race} {char.character_class}</p>
              </li>
            ))}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            <Link to="/create-character"> 
                <ThemedButton variant="green" runeSymbol="+">Create New Character</ThemedButton>
            </Link>
        </div>
      </div>

      {/* Campaigns You DM Section */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You DM</h2>
        {isLoadingDmCampaigns && <p>Loading your campaigns...</p>}
        {dmCampaignError && <p style={{ color: 'red' }}>Error: {dmCampaignError}</p>}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length === 0 && (
          <p>You are not currently running any campaigns.</p>
        )}
        {!isLoadingDmCampaigns && !dmCampaignError && dmCampaigns.length > 0 && (
          <ul style={listStyle}>
            {dmCampaigns.map((camp) => (
              <li key={camp.id} style={listItemStyle}>
                <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                  <Link to={`/campaigns/${camp.id}/manage`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                    {camp.title}
                  </Link>
                </h3>
                <p style={{margin: '5px 0'}}>Status: {camp.is_open_for_recruitment ? "Open for Recruitment" : "Closed"}</p>
                <p style={{margin: '5px 0'}}>{camp.members?.length || 0} member(s)</p>
              </li>
            ))}
          </ul>
        )}
         <div style={{marginTop: '20px'}}>
            <Link to="/create-campaign"> {/* We'll need to create this route & page */}
                <ThemedButton variant="red" runeSymbol="📜">Forge New Campaign</ThemedButton>
            </Link>
        </div>
      </div>

      {/* Campaigns You're In Section */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Campaigns You're In</h2>
        {isLoadingPlayerCampaigns && <p>Loading your active campaigns...</p>}
        {playerCampaignError && <p style={{ color: 'red' }}>Error: {playerCampaignError}</p>}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length === 0 && (
          <p>You have not yet joined any campaigns as a player.</p>
        )}
        {!isLoadingPlayerCampaigns && !playerCampaignError && playerCampaigns.length > 0 && (
          <ul style={listStyle}>
            {playerCampaigns.map((camp) => (
              <li key={camp.id} style={listItemStyle}>
                <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                   <Link to={`/campaigns/${camp.id}/play`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                    {camp.title}
                  </Link>
                </h3>
                <p style={{margin: '5px 0'}}>DM: {camp.dm?.username || 'Unknown'}</p>
                {/* Add link to view campaign details/play area */}
              </li>
            ))}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            <Link to="/discover-campaigns"> {/* We'll need to create this route & page */}
                <ThemedButton variant="green" runeSymbol="🗺️">Discover Campaigns</ThemedButton>
            </Link>
        </div>
      </div>

    </div>
  );
};

export default DashboardPage;

