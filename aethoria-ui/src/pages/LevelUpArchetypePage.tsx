// Path: src/pages/LevelUpArchetypePage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character } from '../types/character';
// Assuming RogueArchetypeSelectionRequest is in types/character.ts or a new types/rogue.ts
import type { RogueArchetypeSelectionRequest } from '../types/character'; 
import ThemedButton from '../components/common/ThemedButton';

// Frontend equivalent or import from a shared types/game_data location later
// For now, hardcoding SRD options. Ensure these string values match backend Enum values.
const AVAILABLE_ROGUE_ARCHETYPES_FRONTEND = [
  { value: "Thief", label: "Thief" },
  { value: "Assassin", label: "Assassin" },
  { value: "Arcane Trickster", label: "Arcane Trickster" },
];
// This should match the RoguishArchetypeEnum string values from your backend
type RogueArchetypeValue = "Thief" | "Assassin" | "Arcane Trickster";


const LevelUpArchetypePage: React.FC = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const auth = useAuth();
  const navigate = useNavigate();

  const [character, setCharacter] = useState<Character | null>(null);
  const [selectedArchetype, setSelectedArchetype] = useState<RogueArchetypeValue | "">("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchCharacterData = async () => {
      if (auth?.token && characterId) {
        setIsLoading(true);
        setError(null);
        setSuccessMessage(null);
        try {
          const charIdNum = parseInt(characterId, 10);
          if (isNaN(charIdNum)) throw new Error("Invalid character ID.");

          const fetchedCharacter = await characterService.getCharacterById(auth.token, charIdNum);
          setCharacter(fetchedCharacter);

          if (fetchedCharacter.character_class?.toLowerCase() !== 'rogue') {
            setError("Archetype selection is for Rogues only.");
          } else if (fetchedCharacter.level < 3) {
            setError(`Rogues choose an archetype at Level 3. Current level: ${fetchedCharacter.level}`);
          } else if (fetchedCharacter.roguish_archetype) {
            setError(`Archetype already selected: ${fetchedCharacter.roguish_archetype}`);
            setSuccessMessage(`Archetype already selected: ${fetchedCharacter.roguish_archetype}. No action needed.`);
          } else if (fetchedCharacter.level_up_status !== 'pending_archetype_selection') {
            setError(`Character not pending archetype selection. Status: ${fetchedCharacter.level_up_status || 'None'}`);
          }
        } catch (err: any) {
          setError(err.message || "Failed to load character data for archetype selection.");
        } finally {
          setIsLoading(false);
        }
      } else if (!auth?.isLoading) {
        setError("Authentication required or character ID missing.");
        setIsLoading(false);
      }
    };
    if (!auth?.isLoading) {
        fetchCharacterData();
    }
  }, [auth?.token, auth?.isLoading, characterId]);

  const handleSubmitArchetype = async () => {
    if (!auth?.token || !characterId || !character || !selectedArchetype) {
      setError("Required information missing or no archetype selected.");
      return;
    }
    if (character.level_up_status !== 'pending_archetype_selection') {
        setError(`Character is not pending archetype selection. Status: ${character.level_up_status || 'None'}.`);
        return;
    }

    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    const payload: RogueArchetypeSelectionRequest = {
      archetype_name: selectedArchetype// Cast, assuming values match backend Enum
    };

    try {
      const charIdNum = parseInt(characterId, 10);
      // We need a characterService.selectRogueArchetype function
      const updatedCharacter = await characterService.selectRogueArchetype(auth.token, charIdNum, payload);
      setCharacter(updatedCharacter); 
      setSuccessMessage(`Archetype "${updatedCharacter.roguish_archetype}" selected! New status: ${updatedCharacter.level_up_status || 'Level up choices complete!'}`);

      setTimeout(() => {
        if (updatedCharacter.level_up_status === 'pending_asi') {
            navigate(`/character/${characterId}/level-up/asi`);
        } else {
          navigate(`/dashboard`); // Or to character sheet
        }
      }, 2500);

    } catch (err: any) {
      setError(err.message || "Failed to select archetype.");
    } finally {
      // setIsLoading(false); // Let navigation or final message handle this
    }
  };

  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '700px', margin: '20px auto', textAlign: 'center' };
  const containerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px', borderRadius: '8px', boxShadow: '0px 4px 12px rgba(0,0,0,0.1)' };
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', marginBottom: '1em'};
  const infoStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', marginBottom: '1.5em'};
  const errorStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(255,0,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid red' };
  const successStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(0,128,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid green' };
  const selectGroupStyle: React.CSSProperties = { margin: '20px 0', textAlign: 'left' };
  const selectLabelStyle: React.CSSProperties = { display: 'block', fontFamily: 'var(--font-script-annotation)', fontSize: '1.1em', color: 'var(--ink-color-medium)', marginBottom: '0.4em' };
  const selectElementStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', fontSize: '1.2em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', cursor: 'pointer', marginBottom: '1em'};

  if (isLoading && !character && !successMessage) { 
    return <div style={pageStyle}><p>Loading Archetype Selection...</p></div>;
  }
  if (error && !successMessage) { 
     return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Rogue Archetype</h1><p style={errorStyle}>{error}</p><Link to="/dashboard" style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }
  if (!character && !isLoading && !successMessage) { 
     return <div style={pageStyle}><p>Could not load character data.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  if (character && character.level_up_status !== 'pending_archetype_selection' && !successMessage) {
    return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Rogue Archetype</h1><p style={infoStyle}>{character.name} (Level {character.level}) is not currently pending archetype selection. Status: {character.level_up_status || 'None'}.</p><Link to={`/dashboard`} style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }

  return (
    <div style={pageStyle}>
      <div style={containerStyle}>
        <h1 style={titleStyle}>Choose Roguish Archetype - {character?.name} (Level {character?.level})</h1>

        {!successMessage && character && character.level_up_status === 'pending_archetype_selection' && (
            <>
                <p style={infoStyle}>
                At 3rd level, you choose an archetype that you emulate in the exercise of your rogue abilities.
                </p>

                <div style={selectGroupStyle}>
                    <label htmlFor="archetype-select" style={selectLabelStyle}>Select your Archetype:</label>
                    <select 
                        id="archetype-select"
                        value={selectedArchetype}
                        onChange={(e) => setSelectedArchetype(e.target.value as RogueArchetypeValue)}
                        style={selectElementStyle}
                        disabled={isLoading}
                    >
                        <option value="">-- Choose Archetype --</option>
                        {AVAILABLE_ROGUE_ARCHETYPES_FRONTEND.map(arch => (
                            <option key={arch.value} value={arch.value}>{arch.label}</option>
                        ))}
                    </select>
                </div>

                {error && <p style={errorStyle}>{error}</p>}

                <div style={{marginTop: '2em'}}>
                <ThemedButton 
                    onClick={handleSubmitArchetype} 
                    disabled={isLoading || !selectedArchetype} 
                    variant="green"
                    runeSymbol="🎭" // Masks for rogue/archetype
                    tooltipText="Confirm Archetype Choice"
                >
                    {isLoading ? "Confirming..." : "Confirm Archetype"}
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

export default LevelUpArchetypePage;