// Path: src/pages/SpellsViewPage.tsx
import React, { useEffect, useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { SpellDefinition } from '../types/spell';
import styles from './SpellsViewPage.module.css';

const SpellsViewPage: React.FC = () => {
  const auth = useAuth();
  const [allSpells, setAllSpells] = useState<SpellDefinition[]>([]);
  const [filteredSpells, setFilteredSpells] = useState<SpellDefinition[]>([]);
  const [selectedSpell, setSelectedSpell] = useState<SpellDefinition | null>(null);

  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSpells = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getSpells(auth.token);
          data.sort((a, b) => a.level - b.level || a.name.localeCompare(b.name));
          setAllSpells(data);
        } catch (err: any) {
          setError(err.message || "Failed to load spell data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadSpells();
  }, [auth.token]);

  useEffect(() => {
    let spellsToFilter = [...allSpells];
    if (selectedLevel !== 'all') {
      spellsToFilter = spellsToFilter.filter(spell => spell.level === parseInt(selectedLevel, 10));
    }
    if (searchTerm) {
      spellsToFilter = spellsToFilter.filter(spell => 
        spell.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    setFilteredSpells(spellsToFilter);
    setSelectedSpell(null);
  }, [selectedLevel, searchTerm, allSpells]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = allSpells.find(s => s.name === selectedName) || null;
    setSelectedSpell(details);
  };
  
  const spellLevels = useMemo(() => {
    const levels = new Set(allSpells.map(s => s.level));
    return Array.from(levels).sort((a,b) => a - b);
  }, [allSpells]);

  if (isLoading) return <div className={styles.pageContainer}><p>Opening the Grimoire...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.title}>Grimoire</h1>
      </header>
      
      <div className={styles.filterContainer}>
        <div className={styles.filterGroup}>
          <label htmlFor="level-selector" className={styles.selectorLabel}>Filter by Level</label>
          <select 
            id="level-selector" 
            onChange={(e) => setSelectedLevel(e.target.value)} 
            value={selectedLevel}
            className={styles.spellSelector}
          >
            <option value="all">All Levels</option>
            {spellLevels.map(level => (
              <option key={level} value={level}>
                {level === 0 ? 'Cantrip' : `Level ${level}`}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.filterGroup}>
          <label htmlFor="search-input" className={styles.selectorLabel}>Search by Name</label>
          <input
            id="search-input"
            type="text"
            placeholder="e.g., Fireball"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.filterInput}
          />
        </div>
      </div>

      <div className={styles.selectorContainer}>
        <label htmlFor="spell-selector" className={styles.selectorLabel}>Select a Spell</label>
        <select id="spell-selector" onChange={handleSelection} className={styles.spellSelector} value={selectedSpell?.name || ""}>
          <option value="" disabled>-- Select a Spell --</option>
          {filteredSpells.map(spell => (
            <option key={spell.id} value={spell.name}>
              {spell.name}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.spellDisplay}>
        {selectedSpell ? (
          <div>
            <h2 className={styles.spellName}>{selectedSpell.name}</h2>
            <p className={styles.spellMeta}>
              {selectedSpell.level > 0 ? `Level ${selectedSpell.level} ${selectedSpell.school}` : `${selectedSpell.school} Cantrip`}
            </p>
            <div className={styles.spellDescription}>
                <p className={styles.spellDetail}><strong>Casting Time:</strong> {selectedSpell.casting_time}</p>
                <p className={styles.spellDetail}><strong>Range:</strong> {selectedSpell.range}</p>
                <p className={styles.spellDetail}><strong>Components:</strong> {selectedSpell.components}</p>
                <p className={styles.spellDetail}><strong>Duration:</strong> {selectedSpell.duration}</p>
                <hr style={{margin: '1em 0', borderTop: '1px solid var(--ink-color-light)'}} />
                <p>{selectedSpell.description}</p>
                {selectedSpell.higher_level && <p><strong>At Higher Levels:</strong> {selectedSpell.higher_level}</p>}
                {/* --- START MODIFICATION --- */}
                <p className={styles.spellClasses}>
                  <strong>Classes:</strong> {selectedSpell.dnd_classes?.join(', ') || 'None'}
                </p>
                {/* --- END MODIFICATION --- */}
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

