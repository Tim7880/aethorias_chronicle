// Path: src/pages/LevelUpArchetypePage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character, RogueArchetypeSelectionRequest } from '../types/character'; 
import ThemedButton from '../components/common/ThemedButton';
import styles from './LevelUpArchetypePage.module.css'; // <--- IMPORT ITS OWN CSS MODULE

const AVAILABLE_ROGUE_ARCHETYPES_FRONTEND = [
  { value: "Thief", label: "Thief", description: "Focuses on speed, agility, and using items quickly." },
  { value: "Assassin", label: "Assassin", description: "Excels at infiltration and dealing deadly strikes to unsuspecting foes." },
  { value: "Arcane Trickster", label: "Arcane Trickster", description: "Supplements roguish skills with illusion and enchantment magic." },
] as const; 

type RogueArchetypeValue = typeof AVAILABLE_ROGUE_ARCHETYPES_FRONTEND[number]['value'];

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
        setIsLoading(true); setError(null); setSuccessMessage(null);
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
            setSuccessMessage(`Archetype already selected: ${fetchedCharacter.roguish_archetype}. No further action needed.`);
            setError(null); 
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
      setError("Required information missing or no archetype selected."); return;
    }
    if (character.level_up_status !== 'pending_archetype_selection') {
        setError(`Character is not pending archetype selection. Status: ${character.level_up_status || 'None'}.`); return;
    }
    if (character.roguish_archetype) {
        setError(`Archetype already selected: ${character.roguish_archetype}.`); return;
    }

    setIsLoading(true); setError(null); setSuccessMessage(null);
    const payload: RogueArchetypeSelectionRequest = { archetype_name: selectedArchetype };

    try {
      const charIdNum = parseInt(characterId, 10);
      const updatedCharacter = await characterService.selectRogueArchetype(auth.token, charIdNum, payload);
      setCharacter(updatedCharacter); 
      setSuccessMessage(`Archetype "${updatedCharacter.roguish_archetype}" selected! New status: ${updatedCharacter.level_up_status || 'Level up choices complete!'}`);
      
      setTimeout(() => {
        if (updatedCharacter.level_up_status === 'pending_asi') {
            navigate(`/character/${characterId}/level-up/asi`);
        } else { 
          navigate(`/dashboard`); 
        }
      }, 3000); // Increased delay slightly

    } catch (err: any) {
      setError(err.message || "Failed to select archetype.");
      setIsLoading(false);
    } 
    // setIsLoading(false) handled by error case or navigation
  };

  if (isLoading && !character && !successMessage) { 
    return <div className={styles.pageStyle}><p>Loading Archetype Selection...</p></div>;
  }
  if (error && !successMessage) { 
     return (<div className={styles.pageStyle}><div className={styles.container}><h1 className={styles.title}>Roguish Archetype</h1><p className={styles.errorText}>{error}</p><Link to="/dashboard" style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }
  if (!character && !isLoading && !successMessage) { 
     return <div className={styles.pageStyle}><p>Could not load character data.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  // If character is loaded but not pending archetype (and no success message from *this* page interaction)
  // Or if archetype was already selected on load
  if (character && (character.level_up_status !== 'pending_archetype_selection' || character.roguish_archetype) && !successMessage) {
    const statusMessage = character.roguish_archetype 
        ? `Archetype already selected: ${character.roguish_archetype}.`
        : `Not currently pending archetype selection. Status: ${character.level_up_status || 'None'}.`;
    return (<div className={styles.pageStyle}><div className={styles.container}><h1 className={styles.title}>Roguish Archetype</h1><p className={styles.infoText}>{character.name} (Level {character.level})</p><p className={styles.infoTextLeft}>{statusMessage}</p><Link to={`/dashboard`} style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }

  return (
    <div className={styles.pageStyle}>
      <div className={styles.container}>
        <h1 className={styles.title}>Choose Roguish Archetype - {character?.name} (Level {character?.level})</h1>
        
        {!successMessage && character && character.level_up_status === 'pending_archetype_selection' && !character.roguish_archetype &&(
            <>
                <p className={styles.infoTextLeft}>
                At 3rd level, you choose an archetype that you emulate in the exercise of your rogue abilities. This choice grants you features at 3rd level and again at later levels.
                </p>

                <div className={styles.selectGroup}>
                    <label htmlFor="archetype-select" className={styles.selectLabel}>Select your Archetype:</label>
                    <select 
                        id="archetype-select"
                        name="archetype_name"
                        value={selectedArchetype}
                        onChange={(e) => setSelectedArchetype(e.target.value as RogueArchetypeValue)}
                        className={styles.selectElement}
                        disabled={isLoading}
                        required
                    >
                        <option value="">-- Choose Archetype --</option>
                        {AVAILABLE_ROGUE_ARCHETYPES_FRONTEND.map(arch => (
                            <option key={arch.value} value={arch.value}>{arch.label.split(" - ")[0]}</option>
                        ))}
                    </select>
                    {selectedArchetype && (
                        <p className={styles.archetypeDescription}>
                            {AVAILABLE_ROGUE_ARCHETYPES_FRONTEND.find(a => a.value === selectedArchetype)?.description || ''}
                        </p>
                    )}
                </div>

                {error && <p className={styles.errorText}>{error}</p>}
                
                <div className={styles.buttonContainer}>
                <ThemedButton 
                    onClick={handleSubmitArchetype} 
                    disabled={isLoading || !selectedArchetype} 
                    variant="green"
                    runeSymbol="🎭" 
                    tooltipText="Confirm Archetype Choice"
                >
                    {isLoading ? "Confirming..." : "Confirm Archetype"}
                </ThemedButton>
                </div>
            </>
        )}
        {successMessage && (
            <>
                <p className={styles.successText}>{successMessage}</p>
                <p className={styles.infoText}>Proceeding with your adventure...</p>
            </>
        )}
      </div>
    </div>
  );
};

export default LevelUpArchetypePage;

