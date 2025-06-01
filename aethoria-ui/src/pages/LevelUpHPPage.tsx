// Path: src/pages/LevelUpHPPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character } from '../types/character';
import ThemedButton from '../components/common/ThemedButton';

// Helper function (can be moved to a utils file later)
const calculate_ability_modifier = (score: number | null | undefined): number => {
  if (score === null || score === undefined) {
    return 0;
  }
  return Math.floor((score - 10) / 2);
};

const LevelUpHPPage: React.FC = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const auth = useAuth();
  const navigate = useNavigate();

  const [character, setCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<'average' | 'roll'>('average');
  const [hpGainedMessage, setHpGainedMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchCharacterForLevelUp = async () => {
      if (auth?.token && characterId) {
        setIsLoading(true);
        setError(null);
        setHpGainedMessage(null);
        try {
          const charIdNum = parseInt(characterId, 10);
          if (isNaN(charIdNum)) {
            throw new Error("Invalid character ID in URL.");
          }
          const fetchedCharacter = await characterService.getCharacterById(auth.token, charIdNum);
          
          if (fetchedCharacter.level_up_status !== 'pending_hp') {
            setError(`Character is not currently pending HP confirmation. Status: ${fetchedCharacter.level_up_status || 'None'}.`);
            // No navigation here; just set error and character to allow UI to display status
          }
          setCharacter(fetchedCharacter);
        } catch (err: any) {
          setError(err.message || "Failed to load character data for level up.");
          setCharacter(null);
        } finally {
          setIsLoading(false);
        }
      } else {
        setError("Authentication required or character ID missing.");
        setIsLoading(false);
      }
    };
    fetchCharacterForLevelUp();
  }, [auth?.token, characterId]);

  const handleSubmitHPChoice = async () => {
    if (!auth?.token || !characterId || !character) {
      setError("Authentication, character ID, or character data is missing.");
      return;
    }
    if (character.level_up_status !== 'pending_hp') {
        setError(`Character is not pending HP confirmation. Current status: ${character.level_up_status || 'None'}.`);
        return;
    }

    setIsLoading(true);
    setError(null);
    setHpGainedMessage(null);

    try {
      const response = await characterService.confirmHPIncrease(
        auth.token, 
        parseInt(characterId, 10), 
        selectedMethod
      );
      
      setHpGainedMessage(response.level_up_message); // Using the message from backend
      setCharacter(response.character); 

      setTimeout(() => {
        // Navigate based on the new status from the updated character in the response
        if (response.character.level_up_status === 'pending_asi') {
          navigate(`/character/${characterId}/level-up/asi`);
        } else if (response.character.level_up_status === 'pending_spells') {
          navigate(`/character/${characterId}/level-up/spells`);
        } else if (response.character.level_up_status === 'pending_expertise') {
            navigate(`/character/${characterId}/level-up/expertise`);
        } else if (response.character.level_up_status === 'pending_archetype_selection') {
            navigate(`/character/${characterId}/level-up/archetype`);
        }
        else { 
          navigate(`/dashboard`); // Or to character sheet: /characters/${characterId}
        }
      }, 2500); // Increased delay to allow reading message
    } catch (err: any) {
      setError(err.message || "Failed to confirm HP increase.");
      setIsLoading(false); // Ensure loading is false on error
    } 
    // setIsLoading(false); // isLoading should be false after navigation or error
  };

  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '600px', margin: '20px auto', textAlign: 'center' };
  const containerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px', borderRadius: '8px', boxShadow: '0px 4px 12px rgba(0,0,0,0.1)' };
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', marginBottom: '1em'};
  const infoStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', marginBottom: '1.5em'};
  const errorStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(255,0,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid red' };
  const successStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(0,128,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid green' };
  const radioGroupStyle: React.CSSProperties = { margin: '20px 0', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' };
  const radioLabelStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', cursor: 'pointer', display: 'inline-flex', alignItems: 'center' };


  if (isLoading && !character && !hpGainedMessage) { 
    return <div style={pageStyle}><p>Loading level up information...</p></div>;
  }
  
  if (error && !hpGainedMessage) { // Show error prominently if initial load failed or submit error before success message
     return (
        <div style={pageStyle}>
            <div style={containerStyle}>
                <h1 style={titleStyle}>Level Up Step</h1>
                <p style={errorStyle}>{error}</p>
                <Link to="/dashboard" style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link>
            </div>
        </div>
     );
  }
  
  if (!character) { 
     return <div style={pageStyle}><p>Could not load character data for level up. Character ID: {characterId}</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  
  if (character.level_up_status !== 'pending_hp' && !hpGainedMessage) {
    return (
        <div style={pageStyle}>
            <div style={containerStyle}>
                <h1 style={titleStyle}>Level Up Choice</h1>
                <p style={infoStyle}>
                    {character.name} (Level {character.level}) is not currently pending an HP confirmation.
                    Current status: {character.level_up_status || 'None'}.
                </p>
                <Link to={`/dashboard`} style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link>
            </div>
        </div>
    );
  }

  // Calculate average HP gain text for display
  const avgHpGainText = character.hit_die_type ? `(${(character.hit_die_type / 2) + 1})` : '(N/A)';

  return (
    <div style={pageStyle}>
      <div style={containerStyle}>
        <h1 style={titleStyle}>Level Up! Increase Hit Points</h1>
        <p style={infoStyle}>
            {character.name} has reached Level {character.level}! <br/>
            Your Hit Die is a d{character.hit_die_type || 'N/A'}. Your Constitution modifier is {calculate_ability_modifier(character.constitution)}.
        </p>
        
        {!hpGainedMessage && (
            <>
                <p style={infoStyle}>How would you like to determine your Hit Point increase for this level?</p>
                <div style={radioGroupStyle}>
                <label style={radioLabelStyle}>
                    <input 
                    type="radio" 
                    name="hpMethod" 
                    value="average" 
                    checked={selectedMethod === 'average'} 
                    onChange={() => setSelectedMethod('average')} 
                    style={{marginRight: '8px'}}
                    disabled={isLoading} 
                    />
                    Take Average HP {avgHpGainText}
                </label>
                <label style={radioLabelStyle}>
                    <input 
                    type="radio" 
                    name="hpMethod" 
                    value="roll" 
                    checked={selectedMethod === 'roll'} 
                    onChange={() => setSelectedMethod('roll')} 
                    style={{marginRight: '8px'}}
                    disabled={isLoading} 
                    />
                    Roll 1d{character.hit_die_type || 'N/A'}
                </label>
                </div>

                {error && <p style={errorStyle}>{error}</p>}
                
                <div style={{marginTop: '2em'}}>
                    <ThemedButton 
                    onClick={handleSubmitHPChoice} 
                    disabled={isLoading} 
                    variant="green"
                    runeSymbol="❤️"
                    tooltipText="Confirm HP Choice"
                    >
                    {isLoading ? "Confirming..." : "Confirm HP"}
                    </ThemedButton>
                </div>
            </>
        )}

        {hpGainedMessage && (
            <>
                <p style={successStyle}>{hpGainedMessage}</p>
                <p style={infoStyle}>Loading next step...</p>
            </>
        )}
      </div>
    </div>
  );
};

export default LevelUpHPPage;

