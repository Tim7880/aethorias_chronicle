// Path: src/pages/MonstersViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { Monster } from '../types/monster';
import styles from './MonstersViewPage.module.css';

const MonstersViewPage: React.FC = () => {
  const auth = useAuth();
  const [monsters, setMonsters] = useState<Monster[]>([]);
  const [selectedMonster, setSelectedMonster] = useState<Monster | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMonsters = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getMonsters(auth.token);
          setMonsters(data);
        } catch (err: any) {
          setError(err.message || "Failed to load monster data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadMonsters();
  }, [auth.token]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = monsters.find(m => m.name === selectedName) || null;
    setSelectedMonster(details);
  };

  if (isLoading) return <div className={styles.pageContainer}><p>Loading Bestiary...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.selectorContainer}>
        <label htmlFor="monster-selector" className={styles.selectorLabel}>Browse the Bestiary</label>
        <select id="monster-selector" onChange={handleSelection} className={styles.monsterSelector} defaultValue="">
          <option value="" disabled>-- Select a Monster --</option>
          {monsters.map(monster => (
            <option key={monster.id} value={monster.name}>{monster.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.monsterDisplay}>
        {selectedMonster ? (
          <div>
            <h2 className={styles.monsterName}>{selectedMonster.name}</h2>
            <p className={styles.monsterMeta}>{selectedMonster.size} {selectedMonster.creature_type}, {selectedMonster.alignment}</p>
            
            <div className={styles.statBlock}>
                <div className={styles.statGrid}>
                    <div className={styles.stat}><strong>Armor Class</strong><span className={styles.statValue}>{selectedMonster.armor_class}</span></div>
                    <div className={styles.stat}><strong>Hit Dice</strong><span className={styles.statValue}>{selectedMonster.hit_dice}</span></div>
                    <div className={styles.stat}><strong>Speed</strong><span className={styles.statValue}>{selectedMonster.speed?.walk || 'N/A'}</span></div>
                </div>
            </div>
            
            <div className={styles.statBlock}>
                <div className={styles.statGrid}>
                    <div className={styles.stat}><strong>STR</strong><span className={styles.statValue}>{selectedMonster.strength}</span></div>
                    <div className={styles.stat}><strong>DEX</strong><span className={styles.statValue}>{selectedMonster.dexterity}</span></div>
                    <div className={styles.stat}><strong>CON</strong><span className={styles.statValue}>{selectedMonster.constitution}</span></div>
                    <div className={styles.stat}><strong>INT</strong><span className={styles.statValue}>{selectedMonster.intelligence}</span></div>
                    <div className={styles.stat}><strong>WIS</strong><span className={styles.statValue}>{selectedMonster.wisdom}</span></div>
                    <div className={styles.stat}><strong>CHA</strong><span className={styles.statValue}>{selectedMonster.charisma}</span></div>
                </div>
            </div>

            <div className={styles.section}>
                {selectedMonster.special_abilities && selectedMonster.special_abilities.length > 0 && selectedMonster.special_abilities.map(ability => (
                    <p key={ability.name} className={styles.abilityBlock}>
                        <strong className={styles.abilityName}>{ability.name}.</strong> {ability.desc}
                    </p>
                ))}
            </div>

            {selectedMonster.actions && selectedMonster.actions.length > 0 && (
                <div className={styles.section}>
                    <h3>Actions</h3>
                    {selectedMonster.actions.map(action => (
                        <p key={action.name} className={styles.abilityBlock}>
                            <strong className={styles.abilityName}>{action.name}.</strong> {action.desc}
                        </p>
                    ))}
                </div>
            )}
          </div>
        ) : (
          <p className={styles.promptText}>Select a monster to view its statistics.</p>
        )}
      </div>
    </div>
  );
};

export default MonstersViewPage;
