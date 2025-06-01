// Path: src/pages/LevelUpExpertisePage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character, CharacterSkill } from '../types/character'; // Assuming CharacterSkill is part of character type
import type { ExpertiseSelectionRequest } from '../types/character'; // Or from a dedicated levelUp types file
import ThemedButton from '../components/common/ThemedButton';

const LevelUpExpertisePage: React.FC = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const auth = useAuth();
  const navigate = useNavigate();

  const [character, setCharacter] = useState<Character | null>(null);
  const [proficientSkills, setProficientSkills] = useState<CharacterSkill[]>([]);
  const [selectedExpertiseIds, setSelectedExpertiseIds] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const ROGUE_EXPERTISE_CHOICES = 2; // Rogues pick 2

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

          if (fetchedCharacter.level_up_status !== 'pending_expertise') {
            setError(`Character not pending expertise selection. Status: ${fetchedCharacter.level_up_status || 'None'}`);
          }
          if (fetchedCharacter.character_class?.toLowerCase() !== 'rogue') {
            setError("Expertise selection is for Rogues only.");
          }

          // Filter for proficient skills that don't already have expertise
          const availableForExpertise = fetchedCharacter.skills.filter(
            s => s.is_proficient && !s.has_expertise
          );
          setProficientSkills(availableForExpertise);

        } catch (err: any) {
          setError(err.message || "Failed to load character data for expertise selection.");
        } finally {
          setIsLoading(false);
        }
      } else {
        setError("Authentication required or character ID missing.");
        setIsLoading(false);
      }
    };
    if (!auth?.isLoading) { // Only fetch if auth is not loading
        fetchCharacterData();
    }
  }, [auth?.token, auth?.isLoading, characterId]);

  const handleSkillToggle = (skillId: number) => {
    setSelectedExpertiseIds(prevSelected => {
      if (prevSelected.includes(skillId)) {
        return prevSelected.filter(id => id !== skillId);
      } else {
        if (prevSelected.length < ROGUE_EXPERTISE_CHOICES) {
          return [...prevSelected, skillId];
        }
        return prevSelected; // Max choices reached
      }
    });
  };

  const handleSubmitExpertise = async () => {
    if (!auth?.token || !characterId || !character) {
      setError("Required information missing.");
      return;
    }
    if (selectedExpertiseIds.length !== ROGUE_EXPERTISE_CHOICES) {
      setError(`Please select exactly ${ROGUE_EXPERTISE_CHOICES} skills for expertise.`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    const payload: ExpertiseSelectionRequest = {
      expert_skill_ids: selectedExpertiseIds
    };

    try {
      const updatedCharacter = await characterService.selectRogueExpertise(auth.token, parseInt(characterId, 10), payload);
      setCharacter(updatedCharacter); // Update local character state
      setSuccessMessage(`Expertise successfully applied to ${selectedExpertiseIds.length} skill(s)! Character status: ${updatedCharacter.level_up_status || 'None'}`);
      
      setTimeout(() => {
        // Navigate based on new status (should be None for L1 Rogue, or next step for L6 Rogue)
        if (updatedCharacter.level_up_status === 'pending_archetype_selection') {
             navigate(`/character/${characterId}/level-up/archetype`);
        } else if (updatedCharacter.level_up_status === 'pending_asi') {
            navigate(`/character/${characterId}/level-up/asi`);
        } else if (updatedCharacter.level_up_status === 'pending_spells') {
            navigate(`/character/${characterId}/level-up/spells`);
        }
         else {
          navigate(`/dashboard`); // Or to character sheet
        }
      }, 2500);

    } catch (err: any) {
      setError(err.message || "Failed to apply expertise.");
    } finally {
      // setIsLoading(false); // Let navigation handle UI change or keep loading if showing success message
    }
  };

  // --- Styling (pageStyle, containerStyle, etc. as before) ---
  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '700px', margin: '20px auto', textAlign: 'center' };
  const containerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px', borderRadius: '8px', boxShadow: '0px 4px 12px rgba(0,0,0,0.1)' };
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', marginBottom: '1em'};
  const infoStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', marginBottom: '1.5em'};
  const errorStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(255,0,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid red' };
  const successStyle: React.CSSProperties = { color: 'var(--ink-color-dark)', backgroundColor: 'rgba(0,128,0,0.1)', padding: '10px', borderRadius: '4px', marginTop: '1em', border: '1px solid green' };
  const skillListStyle: React.CSSProperties = { listStyle: 'none', padding: 0, textAlign: 'left'};
  const skillItemStyle: React.CSSProperties = { marginBottom: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center' };
  const checkboxStyle: React.CSSProperties = { marginRight: '10px', transform: 'scale(1.2)' };


  if (isLoading && !character && !successMessage) { 
    return <div style={pageStyle}><p>Loading Expertise Selection...</p></div>;
  }
  if (error && !successMessage) { 
     return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Expertise Selection</h1><p style={errorStyle}>{error}</p><Link to="/dashboard" style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }
  if (!character) { 
     return <div style={pageStyle}><p>Could not load character data for expertise selection.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  if (character.level_up_status !== 'pending_expertise' && !successMessage) {
    return (<div style={pageStyle}><div style={containerStyle}><h1 style={titleStyle}>Expertise Selection</h1><p style={infoStyle}>{character.name} (Level {character.level}) is not currently pending expertise selection. Status: {character.level_up_status || 'None'}.</p><Link to={`/dashboard`} style={{marginTop: '20px', display: 'inline-block', fontFamily: 'var(--font-body-primary)'}}>Return to Dashboard</Link></div></div>);
  }

  return (
    <div style={pageStyle}>
      <div style={containerStyle}>
        <h1 style={titleStyle}>Choose Expertise - {character.name} (Level {character.level})</h1>
        
        {!successMessage && (
            <>
                <p style={infoStyle}>
                As a Rogue, you gain Expertise. Choose {ROGUE_EXPERTISE_CHOICES} of your skill proficiencies. 
                Your proficiency bonus is doubled for any ability check you make that uses either of the chosen proficiencies.
                </p>

                {proficientSkills.length > 0 ? (
                <ul style={skillListStyle}>
                    {proficientSkills.map(skillAssoc => (
                    <li key={skillAssoc.skill_id} style={skillItemStyle} onClick={() => !isLoading && handleSkillToggle(skillAssoc.skill_id)}>
                        <input 
                        type="checkbox" 
                        id={`skill-expertise-${skillAssoc.skill_id}`}
                        checked={selectedExpertiseIds.includes(skillAssoc.skill_id)}
                        onChange={() => handleSkillToggle(skillAssoc.skill_id)}
                        disabled={isLoading || (selectedExpertiseIds.length >= ROGUE_EXPERTISE_CHOICES && !selectedExpertiseIds.includes(skillAssoc.skill_id))}
                        style={checkboxStyle}
                        />
                        <label htmlFor={`skill-expertise-${skillAssoc.skill_id}`} style={{cursor: 'pointer'}}>
                        {skillAssoc.skill_definition.name}
                        </label>
                    </li>
                    ))}
                </ul>
                ) : (
                <p>No skills available for expertise. Ensure you have skill proficiencies assigned.</p>
                )}

                <p style={{fontFamily: 'var(--font-body-primary)', fontSize: '0.9em', marginTop: '1em'}}>
                    Selected: {selectedExpertiseIds.length} / {ROGUE_EXPERTISE_CHOICES}
                </p>

                {error && <p style={errorStyle}>{error}</p>}
                
                <div style={{marginTop: '2em'}}>
                <ThemedButton 
                    onClick={handleSubmitExpertise} 
                    disabled={isLoading || selectedExpertiseIds.length !== ROGUE_EXPERTISE_CHOICES} 
                    variant="green"
                    runeSymbol="🌟" // Star for expertise
                    tooltipText="Confirm Expertise Choices"
                >
                    {isLoading ? "Confirming..." : "Confirm Expertise"}
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

export default LevelUpExpertisePage;