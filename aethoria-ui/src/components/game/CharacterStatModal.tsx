// Path: src/components/game/CharacterStatModal.tsx
import React from 'react';
import type { Character } from '../../types/character';
import styles from './CharacterStatModal.module.css';

interface CharacterStatModalProps {
  character: Character | null;
  onClose: () => void;
}

const calculateModifier = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return '+0';
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
};

const CharacterStatModal: React.FC<CharacterStatModalProps> = ({ character, onClose }) => {
  if (!character) {
    return null; // Don't render anything if no character is selected
  }

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} className={styles.closeButton} aria-label="Close">&times;</button>
        
        <header className={styles.characterHeader}>
          <h1 className={styles.characterName}>{character.name}</h1>
          <p className={styles.characterSubheader}>
            Level {character.level} {character.race} {character.character_class}
          </p>
        </header>

        <div className={styles.statsGrid}>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>Armor Class</span>
                <span className={styles.statValue}>{character.armor_class || 10}</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>Hit Points</span>
                <span className={styles.statValue}>{character.hit_points_current} / {character.hit_points_max}</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>Speed</span>
                <span className={styles.statValue}>30 ft</span> {/* Placeholder, would need to come from race data */}
            </div>
        </div>
        
        <hr style={{ border: 'none', borderTop: '1px solid var(--ink-color-light)', margin: '1.5rem 0' }} />

        <div className={styles.statsGrid}>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>STR</span>
                <span className={styles.statValue}>{character.strength} ({calculateModifier(character.strength)})</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>DEX</span>
                <span className={styles.statValue}>{character.dexterity} ({calculateModifier(character.dexterity)})</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>CON</span>
                <span className={styles.statValue}>{character.constitution} ({calculateModifier(character.constitution)})</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>INT</span>
                <span className={styles.statValue}>{character.intelligence} ({calculateModifier(character.intelligence)})</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>WIS</span>
                <span className={styles.statValue}>{character.wisdom} ({calculateModifier(character.wisdom)})</span>
            </div>
            <div className={styles.statBox}>
                <span className={styles.statLabel}>CHA</span>
                <span className={styles.statValue}>{character.charisma} ({calculateModifier(character.charisma)})</span>
            </div>
        </div>

      </div>
    </div>
  );
};

export default CharacterStatModal;