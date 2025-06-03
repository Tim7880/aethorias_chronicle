// Path: src/pages/CharacterSheetPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import type { Character } from '../types/character'; // Ensure this path is correct
import styles from './CharacterSheetPage.module.css'; // Your CSS Module

// Helper functions (keep these or move to a utils file)
const calculateAbilityModifier = (score: number | null | undefined): number => {
    if (score === null || score === undefined) return 0;
    return Math.floor((score - 10) / 2);
};
const calculateAbilityModifierDisplay = (score: number | null | undefined): string => {
    const modifier = calculateAbilityModifier(score);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
};
const calculateProficiencyBonus = (level: number): number => {
  if (level < 1) return 2; // Should ideally not happen for valid levels
  return Math.floor((level - 1) / 4) + 2;
};

type AbilityScoreKey = 'strength' | 'dexterity' | 'constitution' | 'intelligence' | 'wisdom' | 'charisma';

const CharacterSheetPage: React.FC = () => {
  const { characterIdFromRoute } = useParams<{ characterIdFromRoute: string }>();
  const auth = useAuth();
  const [character, setCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [proficiencyBonus, setProficiencyBonus] = useState(0);

  useEffect(() => {
    const fetchCharacterSheet = async () => {
      if (auth?.token && characterIdFromRoute) {
        setIsLoading(true); setError(null);
        try {
          const charIdNum = parseInt(characterIdFromRoute, 10);
          if (isNaN(charIdNum)) throw new Error("Invalid character ID.");
          
          const fetchedCharacter = await characterService.getCharacterById(auth.token, charIdNum);
          setCharacter(fetchedCharacter);
          if (fetchedCharacter) {
            setProficiencyBonus(calculateProficiencyBonus(fetchedCharacter.level));
          }
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

    if (!auth?.isLoading) { // Only fetch if auth context is not in its initial loading state
        fetchCharacterSheet();
    }
  }, [auth?.token, auth?.isLoading, characterIdFromRoute]);

  const getLevelUpAction = (char: Character | null): { path: string; text: string } | null => {
    if (!char || !char.level_up_status) return null;
    const charId = char.id; 
    let actionText = "Continue"; // Generic default
    let path = "";
    switch (char.level_up_status) {
      case "pending_hp": path = `/character/${charId}/level-up/hp`; actionText = "Confirm HP"; break;
      case "pending_expertise": path = `/character/${charId}/level-up/expertise`; actionText = "Select Expertise"; break;
      case "pending_archetype_selection": path = `/character/${charId}/level-up/archetype`; actionText = "Choose Archetype"; break;
      case "pending_asi": path = `/character/${charId}/level-up/asi`; actionText = "Select ASI"; break;
      case "pending_spells": path = `/character/${charId}/level-up/spells`; actionText = "Select Spells"; break;
      default: return null;
    }
    return { path, text: actionText };
  };

  const abilityScoresData: Array<{ name: AbilityScoreKey; label: string }> = [
    { name: 'strength', label: 'STR' }, { name: 'dexterity', label: 'DEX' },
    { name: 'constitution', label: 'CON' }, { name: 'intelligence', label: 'INT' },
    { name: 'wisdom', label: 'WIS' }, { name: 'charisma', label: 'CHA' },
  ];

  if (isLoading) {
    return <div className={styles.pageStyle}><p>Loading character sheet...</p></div>;
  }
  if (error) {
    return <div className={styles.pageStyle}><p className={styles.errorText}>Error: {error}</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }
  if (!character) {
    return <div className={styles.pageStyle}><p>Character not found.</p><Link to="/dashboard">Return to Dashboard</Link></div>;
  }

  const levelUpAction = getLevelUpAction(character);

  return (
    <div className={styles.pageStyle}>
      {/* Outer div for the wavy edge filter and textured background */}
      <div className={styles.sheetContainerWithWavyEffect}> {/* This div's ::before will have the filter */}
        <div className={styles.sheetContent}>
          
          <header className={styles.pageHeader}>
            <h1>{character.name}</h1>
            <p>
              Level {character.level} {character.race || 'N/A'} {character.character_class || 'N/A'} 
              {character.roguish_archetype ? ` (${character.roguish_archetype})` : ''}
              <br/>
              {character.alignment || 'N/A'} | XP: {character.experience_points ?? 0} | Proficiency Bonus: <span style={{fontWeight:'bold'}}>+{proficiencyBonus}</span>
            </p>
          </header>

          {levelUpAction && (
              <div className={styles.levelUpNotification}>
                  <Link to={levelUpAction.path} className={styles.levelUpLink}>
                      LEVEL UP! Click here to: {levelUpAction.text} ⬆️
                  </Link>
              </div>
          )}

          <div className={styles.box}>
              <h2 className={styles.sectionTitle}>Ability Scores</h2>
              <div className={styles.abilitiesSection}>
                  {abilityScoresData.map(scoreInfo => (
                      <div key={scoreInfo.name} className={styles.abilityScoreBox}>
                          <div className={styles.abilityScoreLabel}>{scoreInfo.label}</div>
                          <div className={styles.abilityScoreValue}>{(character[scoreInfo.name] as number) ?? '-'}</div>
                          <div className={styles.abilityScoreModifier}>
                              {calculateAbilityModifierDisplay(character[scoreInfo.name] as number | null)}
                          </div>
                      </div>
                  ))}
              </div>
          </div>
          
          <div className={styles.mainGridContainer}>
            <div className={styles.box}>
              <h2 className={styles.sectionTitle}>Combat</h2>
              <ul className={styles.statList}>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Armor Class:</span> <span className={styles.statItemValue}>{character.armor_class ?? 'N/A'}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Hit Points:</span> <span className={styles.statItemValue}>{character.hit_points_current ?? 'N/A'} / {character.hit_points_max ?? 'N/A'}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Hit Dice:</span> <span className={styles.statItemValue}>{character.hit_dice_remaining}/{character.hit_dice_total} (d{character.hit_die_type || 'N/A'})</span></li>
                  <li className={`${styles.statItem} ${styles.lastStatItemInList || ''}`}><span className={styles.statItemLabel}>Initiative:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.dexterity)}</span></li>
              </ul>
              <h3 style={{fontFamily: 'var(--font-script-annotation)', marginTop: '20px', marginBottom: '8px', color: 'var(--ink-color-medium)', fontSize: '1.3em'}}>Death Saves</h3>
              <ul className={styles.statList}>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Successes:</span> <span className={styles.statItemValue}>{character.death_save_successes}</span></li>
                  <li className={`${styles.statItem} ${styles.lastStatItemInList || ''}`}><span className={styles.statItemLabel}>Failures:</span> <span className={styles.statItemValue}>{character.death_save_failures}</span></li>
              </ul>
            </div>

            <div className={styles.box}> 
              <h2 className={styles.sectionTitle}>Saving Throws</h2>
              <ul className={styles.statList}>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Strength:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.strength)}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Dexterity:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.dexterity)}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Constitution:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.constitution)}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Intelligence:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.intelligence)}</span></li>
                  <li className={styles.statItem}><span className={styles.statItemLabel}>Wisdom:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.wisdom)}</span></li>
                  <li className={`${styles.statItem} ${styles.lastStatItemInList || ''}`}><span className={styles.statItemLabel}>Charisma:</span> <span className={styles.statItemValue}>{calculateAbilityModifierDisplay(character.charisma)}</span></li>
              </ul>
              <p style={{fontSize:'0.9em', color: 'var(--ink-color-light)', marginTop: '10px'}}>(Proficiencies not yet applied)</p>
            </div>
          </div>
          
          <div className={styles.box} style={{marginTop: '0px'}}> {/* Adjusted margin if mainGridContainer handles bottom margin */}
            <h2 className={styles.sectionTitle}>Skills</h2>
            {character.skills && character.skills.length > 0 ? (
              <ul className={styles.skillsListThreeColumn}> {/* Using the 3-column style */}
                {character.skills.sort((a,b) => a.skill_definition.name.localeCompare(b.skill_definition.name)).map(skillAssoc => {
                  const abilityName = skillAssoc.skill_definition.ability_modifier_name.toLowerCase() as AbilityScoreKey; 
                  const abilityScore = character[abilityName] as number | null | undefined; 
                  const abilityMod = calculateAbilityModifier(abilityScore);
                  let skillMod = abilityMod;
                  if (skillAssoc.is_proficient) skillMod += proficiencyBonus;
                  if (skillAssoc.has_expertise) skillMod += proficiencyBonus; 
                  
                  return (
                    <li key={skillAssoc.skill_id} className={styles.skillItem}>
                      <div className={styles.skillNameContainer}>
                        <span className={styles.skillProficiencySymbol}>{skillAssoc.is_proficient ? '●' : '○'}</span>
                        {skillAssoc.has_expertise && <span className={styles.skillExpertiseSymbol}>✶</span>} 
                        {skillAssoc.skill_definition.name} 
                        <span className={styles.skillAbilityHint}> ({skillAssoc.skill_definition.ability_modifier_name})</span>
                      </div>
                      <span className={styles.statValue}>{skillMod >= 0 ? `+${skillMod}` : skillMod}</span>
                    </li>
                  );
                })}
              </ul>
            ) : <p>No skills assigned.</p>}
          </div>
          
          <div className={styles.mainGridContainer} style={{marginTop: '25px'}}>
              <div className={styles.box}>
                  <h2 className={styles.sectionTitle}>Known Spells</h2>
                  {character.known_spells && character.known_spells.length > 0 ? (
                      <ul className={styles.statList}>
                      {character.known_spells
                          .sort((a,b) => a.spell_definition.level - b.spell_definition.level || a.spell_definition.name.localeCompare(b.spell_definition.name))
                          .map(charSpell => (
                          <li key={charSpell.id} className={styles.statItem}>
                              <span title={charSpell.spell_definition.description}>
                                  {charSpell.spell_definition.name} 
                                  <span style={{fontSize: '0.8em', color: '#777'}}> (L{charSpell.spell_definition.level})</span>
                              </span>
                              <span style={{fontSize: '0.9em', color: 'var(--ink-color-medium)'}}>
                                  {charSpell.is_known && "Known"}
                                  {charSpell.is_known && charSpell.is_prepared && ", "}
                                  {charSpell.is_prepared && "Prepared"}
                              </span>
                          </li>
                      ))}
                      </ul>
                  ) : <p>No spells known.</p>}
              </div>

               <div className={styles.box}> {/* Inventory and Currency Box */}
                  <h2 className={styles.sectionTitle}>Inventory & Wealth</h2>
                  <div className={styles.inventoryHeader}>
                      <span className={styles.inventoryHeaderName}>Item</span>
                      <span className={styles.inventoryHeaderQuantity}>Qty</span>
                  </div>
                  {character.inventory_items && character.inventory_items.length > 0 ? (
                      <ul className={styles.statList}>
                      {character.inventory_items.map(invItem => (
                          <li key={invItem.id} className={styles.statItem}>
                            <span className={styles.inventoryItemName} title={invItem.item_definition.description || invItem.item_definition.name}>
                                {invItem.item_definition.name} {invItem.is_equipped ? "[E]" : ""}
                            </span>
                            <span className={styles.inventoryItemQuantity}>{invItem.quantity}</span>
                          </li>
                      ))}
                      </ul>
                  ) : <p>Inventory is empty.</p>}
                  
                  {/* --- NEW: Currency Display --- */}
                  <div className={styles.currencyDisplay}>
                    <span className={styles.currencyItem}>PP: {character.currency_pp ?? 0}</span>
                    <span className={styles.currencyItem}>GP: {character.currency_gp ?? 0}</span>
                    <span className={styles.currencyItem}>EP: {character.currency_ep ?? 0}</span>
                    <span className={styles.currencyItem}>SP: {character.currency_sp ?? 0}</span>
                    <span className={styles.currencyItem}>CP: {character.currency_cp ?? 0}</span>
                  </div>
                  {/* --- END NEW: Currency Display --- */}
              </div>
          </div>
          
          <div className={styles.box} style={{marginTop: '25px'}}>
              <h2 className={styles.sectionTitle}>Description & Story</h2>
              <h3 style={{fontFamily: 'var(--font-script-annotation)', marginTop: '15px', marginBottom: '5px', color: 'var(--ink-color-medium)'}}>Appearance</h3>
              <p className={styles.descriptionBox}>{character.appearance_description || "No appearance described."}</p>
              <h3 style={{fontFamily: 'var(--font-script-annotation)', marginTop: '1em', marginBottom: '5px', color: 'var(--ink-color-medium)'}}>Background Story</h3>
              <p className={styles.descriptionBox}>{character.background_story || "No background story written."}</p>
          </div>

          <div style={{marginTop: '30px', textAlign: 'center'}}>
              <Link to="/dashboard" style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-dark)', fontSize: '1.1em', padding: '8px 15px', border: '1px solid var(--ink-color-medium)', borderRadius: '4px', textDecoration: 'none'}}>
                  Return to Dashboard
              </Link>
          </div>
        </div> {/* End of .sheetContent */}
      </div> {/* End of .sheetContainerWithWavyEffect (or .sheetContainer if you renamed in CSS) */}
    </div>
  );
};

export default CharacterSheetPage;

