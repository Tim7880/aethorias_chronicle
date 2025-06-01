// Path: src/pages/LevelUpASIPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character, ASISelectionRequest } from '../types/character'; // Ensure ASISelectionRequest is here
import ThemedButton from '../components/common/ThemedButton';
// import ThemedInput from '../components/common/ThemedInput'; // If using for direct stat input (less ideal for ASI choice)

// Helper function (can be moved to a utils file later)
const calculateAbilityModifierDisplay = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return "+0";
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
};

const ABILITY_SCORES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"] as const;
type AbilityScoreName = typeof ABILITY_SCORES[number];

const LevelUpASIPage: React.FC = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const auth = useAuth();
  const navigate = useNavigate();

  const [character, setCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // State for ASI selection
  const [asiChoiceType, setAsiChoiceType] = useState<'plusTwo' | 'plusOnePair'>('plusTwo');
  const [primaryStat, setPrimaryStat] = useState<AbilityScoreName | ''>('');
  const [secondaryStat, setSecondaryStat] = useState<AbilityScoreName | ''>('');

  useEffect(() => {
    const fetchCharacterData = async () => {
      if (auth?.token && characterId) {
        setIsLoading(true); setError(null); setSuccessMessage(null);
        try {
          const charIdNum = parseInt(characterId, 10);
          if (isNaN(charIdNum)) throw new Error("Invalid character ID.");
          
          const fetchedCharacter = await characterService.getCharacterById(auth.token, charIdNum);
          setCharacter(fetchedCharacter);

          if (fetchedCharacter.level_up_status !== 'pending_asi') {
            setError(`Character not pending ASI selection. Status: ${fetchedCharacter.level_up_status || 'None'}`);
          }
        } catch (err: any) {
          setError(err.message || "Failed to load character data for ASI selection.");
        } finally {
          setIsLoading(false);
        }
      } else if (!auth?.isLoading) {
        setError("Authentication required or character ID missing.");
        setIsLoading(false);
      }
    };
    if(!auth?.isLoading) fetchCharacterData();
  }, [auth?.token, auth?.isLoading, characterId]);

  const handleSubmitASI = async () => {
    if (!auth?.token || !characterId || !character) {
      setError("Required information missing."); return;
    }
    if (character.level_up_status !== 'pending_asi') {
        setError(`Character is not pending ASI. Status: ${character.level_up_status || 'None'}.`); return;
    }

    let statIncreases: Record<string, number> = {};
    if (asiChoiceType === 'plusTwo') {
      if (!primaryStat) { setError("Please select a primary stat for +2 increase."); return; }
      statIncreases[primaryStat] = 2;
    } else { // plusOnePair
      if (!primaryStat || !secondaryStat) { setError("Please select two different stats for +1 increase each."); return; }
      if (primaryStat === secondaryStat) { setError("Primary and secondary stats for +1/+1 must be different."); return; }
      statIncreases[primaryStat] = 1;
      statIncreases[secondaryStat] = 1;
    }

    const payload: ASISelectionRequest = { stat_increases: statIncreases };

    setIsLoading(true); setError(null); setSuccessMessage(null);
    try {
      const charIdNum = parseInt(characterId, 10);
      // We need a characterService.selectASI function
      const updatedCharacter = await characterService.selectASI(auth.token, charIdNum, payload);
      setCharacter(updatedCharacter);
      setSuccessMessage(`Ability Score Increase applied! New status: ${updatedCharacter.level_up_status || 'Level up choices complete!'}`);
      
      setTimeout(() => {
        if (updatedCharacter.level_up_status === 'pending_spells') {
          navigate(`/character/${characterId}/level-up/spells`);
        } else if (updatedCharacter.level_up_status === 'pending_expertise') {
          navigate(`/character/${characterId}/level-up/expertise`);
        } else {
          navigate(`/dashboard`); // Or to character sheet
        }
      }, 2500);
    } catch (err: any) {
      setError(err.message || "Failed to apply ASI.");
    } finally {
      // setIsLoading(false); // Let navigation handle
    }
  };

  // Styling (similar to other level up pages)
  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '700px', margin: '20px auto', textAlign: 'center' };
  const containerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px', borderRadius: '8px', boxShadow: '0px 4px 12px rgba(0,0,0,0.1)' };
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', marginBottom: '1em'};
  const infoStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', marginBottom: '1.5em'};
  const errorStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(255,0,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid red' };
  const successStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(0,128,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid green' };
  const selectGroupStyle: React.CSSProperties = { margin: '20px 0', textAlign: 'left' };
  const selectLabelStyle: React.CSSProperties = { display: 'block', fontFamily: 'var(--font-script-annotation)', fontSize: '1.1em', color: 'var(--ink-color-medium)', marginBottom: '0.4em' };
  const selectElementStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', fontSize: '1.2em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', cursor: 'pointer', marginBottom: '1em'};
  const radioGroupStyle: React.CSSProperties = { margin: '20px 0', textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' };
  const radioLabelStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', cursor: 'pointer', display: 'inline-flex', alignItems: 'center' };


  if (isLoading && !character && !successMessage) { 
    return <div style={pageStyle}><p>Loading ASI Selection...</p></div>;
  }
  if (error && !successMessage) { 
     return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Ability Score Increase</h1><p style={errorStyle}>{error}</p><Link to="/dashboard" style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }
  if (!character && !isLoading && !successMessage) { 
     return <div style={pageStyle}><p>Could not load character data for ASI.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  if (character && character.level_up_status !== 'pending_asi' && !successMessage) {
    return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Ability Score Increase</h1><p style={infoStyle}>{character.name} (Level {character.level}) is not currently pending an ASI. Status: {character.level_up_status || 'None'}.</p><Link to={`/dashboard`} style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }

  return (
    <div style={pageStyle}>
      <div style={containerStyle}>
        <h1 style={titleStyle}>Ability Score Increase - {character?.name} (Level {character?.level})</h1>
        
        {!successMessage && character && character.level_up_status === 'pending_asi' && (
            <>
                <p style={infoStyle}>
                    You can increase one ability score by 2, or two ability scores by 1 each.
                </p>

                <div style={radioGroupStyle}>
                    <label style={radioLabelStyle}>
                        <input type="radio" name="asiType" value="plusTwo" checked={asiChoiceType === 'plusTwo'} onChange={() => setAsiChoiceType('plusTwo')} style={{marginRight: '8px'}}/>
                        +2 to one ability score
                    </label>
                    <label style={radioLabelStyle}>
                        <input type="radio" name="asiType" value="plusOnePair" checked={asiChoiceType === 'plusOnePair'} onChange={() => setAsiChoiceType('plusOnePair')} style={{marginRight: '8px'}}/>
                        +1 to two different ability scores
                    </label>
                </div>

                {asiChoiceType === 'plusTwo' && (
                    <div style={selectGroupStyle}>
                        <label htmlFor="primaryStat" style={selectLabelStyle}>Choose stat for +2:</label>
                        <select id="primaryStat" value={primaryStat} onChange={(e) => setPrimaryStat(e.target.value as AbilityScoreName)} style={selectElementStyle} required>
                            <option value="">-- Select Stat --</option>
                            {ABILITY_SCORES.map(stat => <option key={stat} value={stat}>{stat.charAt(0).toUpperCase() + stat.slice(1)}</option>)}
                        </select>
                    </div>
                )}

                {asiChoiceType === 'plusOnePair' && (
                    <>
                        <div style={selectGroupStyle}>
                            <label htmlFor="primaryStatPlusOne" style={selectLabelStyle}>Choose first stat for +1:</label>
                            <select id="primaryStatPlusOne" value={primaryStat} onChange={(e) => setPrimaryStat(e.target.value as AbilityScoreName)} style={selectElementStyle} required>
                                <option value="">-- Select First Stat --</option>
                                {ABILITY_SCORES.map(stat => <option key={`p-${stat}`} value={stat}>{stat.charAt(0).toUpperCase() + stat.slice(1)}</option>)}
                            </select>
                        </div>
                        <div style={selectGroupStyle}>
                            <label htmlFor="secondaryStatPlusOne" style={selectLabelStyle}>Choose second stat for +1:</label>
                            <select id="secondaryStatPlusOne" value={secondaryStat} onChange={(e) => setSecondaryStat(e.target.value as AbilityScoreName)} style={selectElementStyle} required>
                                <option value="">-- Select Second Stat --</option>
                                {ABILITY_SCORES.filter(s => s !== primaryStat).map(stat => <option key={`s-${stat}`} value={stat}>{stat.charAt(0).toUpperCase() + stat.slice(1)}</option>)}
                            </select>
                        </div>
                    </>
                )}

                {error && <p style={errorStyle}>{error}</p>}
                
                <div style={{marginTop: '2em'}}>
                <ThemedButton 
                    onClick={handleSubmitASI} 
                    disabled={isLoading || (asiChoiceType === 'plusTwo' && !primaryStat) || (asiChoiceType === 'plusOnePair' && (!primaryStat || !secondaryStat || primaryStat === secondaryStat))}
                    variant="green"
                    runeSymbol="📈" // Graph increase for ASI
                    tooltipText="Confirm Ability Score Increase"
                >
                    {isLoading ? "Confirming..." : "Confirm ASI"}
                </ThemedButton>
                </div>
            </>
        )}
        {successMessage && (
            <>
                <p style={successStyle}>{successMessage}</p>
                <p style={infoStyle}>Loading next step or returning to dashboard...</p>
            </>
        )}
      </div>
    </div>
  );
};

export default LevelUpASIPage;

