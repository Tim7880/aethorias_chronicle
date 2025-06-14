// Path: src/pages/SpellsViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { SpellDefinition } from '../types/spell';
import styles from './SpellsViewPage.module.css';

const SpellsViewPage: React.FC = () => {
  const auth = useAuth();
  const [spells, setSpells] = useState<SpellDefinition[]>([]);
  const [selectedSpell, setSelectedSpell] = useState<SpellDefinition | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSpells = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getSpells(auth.token);
          // Sort spells by level, then alphabetically
          data.sort((a, b) => a.level - b.level || a.name.localeCompare(b.name));
          setSpells(data);
        } catch (err: any) {
          setError(err.message || "Failed to load spell data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadSpells();
  }, [auth.token]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = spells.find(s => s.name === selectedName) || null;
    setSelectedSpell(details);
  };

  if (isLoading) return <div className={styles.pageContainer}><p>Opening the Grimoire...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.selectorContainer}>
        <label htmlFor="spell-selector" className={styles.selectorLabel}>Search the Grimoire</label>
        <select id="spell-selector" onChange={handleSelection} className={styles.spellSelector} defaultValue="">
          <option value="" disabled>-- Select a Spell --</option>
          {spells.map(spell => (
            <option key={spell.id} value={spell.name}>
              {spell.name} (Lvl {spell.level})
            </option>
          ))}
        </select>
      </div>

      <div className={styles.spellDisplay}>
        {selectedSpell ? (
          <div>
            <h2 className={styles.spellName}>{selectedSpell.name}</h2>
            <p className={styles.spellMeta}>
              {selectedSpell.level > 0 ? `Level ${selectedSpell.level} ${selectedSpell.school.toLowerCase()}` : `${selectedSpell.school} cantrip`}
            </p>
            <div className={styles.spellDescription}>
                <p className={styles.spellDetail}><strong>Casting Time:</strong> {selectedSpell.casting_time}</p>
                <p className={styles.spellDetail}><strong>Range:</strong> {selectedSpell.range}</p>
                <p className={styles.spellDetail}><strong>Components:</strong> {selectedSpell.components}</p>
                <p className={styles.spellDetail}><strong>Duration:</strong> {selectedSpell.duration}</p>
                <hr style={{margin: '1em 0', borderTop: '1px solid var(--ink-color-light)'}} />
                <p>{selectedSpell.description}</p>
                {selectedSpell.higher_level && <p><strong>At Higher Levels:</strong> {selectedSpell.higher_level}</p>}
            </div>
          </div>
        ) : (
          <p className={styles.promptText}>Select a spell from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default SpellsViewPage;
