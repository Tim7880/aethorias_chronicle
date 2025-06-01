// Path: src/pages/CharacterSheetPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character } from '../types/character';

// Helper to calculate ability modifier (can be moved to a utils file later)
const calculateAbilityModifierDisplay = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return "+0";
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
};

const CharacterSheetPage: React.FC = () => {
  const { characterIdFromRoute } = useParams<{ characterIdFromRoute: string }>();
  const auth = useAuth();
  const [character, setCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCharacterSheet = async () => {
      if (auth?.token && characterIdFromRoute) {
        setIsLoading(true);
        setError(null);
        try {
          const charIdNum = parseInt(characterIdFromRoute, 10);
          if (isNaN(charIdNum)) {
            throw new Error("Invalid character ID in URL.");
          }
          const fetchedCharacter = await characterService.getCharacterById(auth.token, charIdNum);
          setCharacter(fetchedCharacter);
        } catch (err: any) {
          setError(err.message || "Failed to load character sheet.");
        } finally {
          setIsLoading(false);
        }
      } else if (!auth?.isLoading) {
        setError("Authentication required or character ID missing.");
        setIsLoading(false);
      }
    };

    if (!auth?.isLoading) {
        fetchCharacterSheet();
    }
  }, [auth?.token, auth?.isLoading, characterIdFromRoute]);

  const pageStyle: React.CSSProperties = { padding: '20px', fontFamily: 'var(--font-body-primary)' };
  const sheetContainerStyle: React.CSSProperties = { 
    backgroundColor: 'var(--parchment-highlight)', 
    border: '1px solid var(--ink-color-light)', 
    borderRadius: '8px', 
    padding: '20px', 
    boxShadow: '0px 4px 12px rgba(0,0,0,0.1)',
    maxWidth: '900px',
    margin: '0 auto'
  };
  const sectionTitleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', borderBottom: '1px solid var(--ink-color-light)', paddingBottom: '0.2em', marginBottom: '0.8em', fontSize: '2em'};
  const errorStyle: React.CSSProperties = { color: 'red' };

  if (isLoading) {
    return <div style={pageStyle}><p>Loading character sheet...</p></div>;
  }
  if (error) {
    return <div style={pageStyle}><p style={errorStyle}>Error: {error}</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  if (!character) {
    return <div style={pageStyle}><p>Character not found.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }

  // Basic display - we will make this much more detailed later
  return (
    <div style={pageStyle}>
      <div style={sheetContainerStyle}>
        <h1 style={{...sectionTitleStyle, fontSize: '2.8em', textAlign: 'center'}}>{character.name}</h1>
        <p>Level {character.level} {character.race} {character.character_class}</p>
        <p>XP: {character.experience_points ?? 0}</p>
        {character.level_up_status && (
            <p style={{color: 'green', fontWeight: 'bold'}}>Level Up Status: {character.level_up_status}</p>
        )}

        <h2 style={sectionTitleStyle}>Ability Scores</h2>
        <ul>
            <li>Strength: {character.strength} ({calculateAbilityModifierDisplay(character.strength)})</li>
            <li>Dexterity: {character.dexterity} ({calculateAbilityModifierDisplay(character.dexterity)})</li>
            <li>Constitution: {character.constitution} ({calculateAbilityModifierDisplay(character.constitution)})</li>
            <li>Intelligence: {character.intelligence} ({calculateAbilityModifierDisplay(character.intelligence)})</li>
            <li>Wisdom: {character.wisdom} ({calculateAbilityModifierDisplay(character.wisdom)})</li>
            <li>Charisma: {character.charisma} ({calculateAbilityModifierDisplay(character.charisma)})</li>
        </ul>

        <h2 style={sectionTitleStyle}>Combat</h2>
        <p>Max HP: {character.hit_points_max}</p>
        <p>Current HP: {character.hit_points_current}</p>
        <p>AC: {character.armor_class}</p>
        <p>Hit Dice: {character.hit_dice_remaining}/{character.hit_dice_total} (d{character.hit_die_type})</p>
        <p>Death Saves: {character.death_save_successes} Successes, {character.death_save_failures} Failures</p>

        {/* We will add sections for skills, inventory, spells, features etc. later */}

        <div style={{marginTop: '20px'}}>
            <Link to="/dashboard" style={{fontFamily: 'var(--font-body-primary)'}}>Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
};

export default CharacterSheetPage;