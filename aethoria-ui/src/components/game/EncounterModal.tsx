// Path: src/components/game/EncounterModal.tsx
import React, { useState, useEffect } from 'react';
import type { CampaignMember } from '../../types/campaign';
import type { Monster } from '../../types/monster';
import ThemedButton from '../common/ThemedButton';
import styles from './EncounterModal.module.css';
export interface Combatant {
  id: string; // Can be 'char_1' or 'Goblin'
  name: string;
  roll: number;
}
interface EncounterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (combatants: Combatant[]) => void;
  players: CampaignMember[];
  monsters: Monster[];
}

const EncounterModal: React.FC<EncounterModalProps> = ({ isOpen, onClose, onSubmit, players, monsters }) => {
  const [combatants, setCombatants] = useState<Combatant[]>([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [initiativeRoll, setInitiativeRoll] = useState('');

  useEffect(() => {
    if (isOpen) {
      setCombatants([]);
      setSelectedTarget('');
      setInitiativeRoll('');
    }
  }, [isOpen]); // This effect runs whenever the 'isOpen' prop changes.--

  if (!isOpen) return null;

  const handleAddCombatant = (e: React.FormEvent) => {
    e.preventDefault();
    const roll = parseInt(initiativeRoll, 10);
    if (!selectedTarget || isNaN(roll)) {
      alert('Please select a creature and enter a valid initiative roll.');
      return;
    }

    const isCharacter = selectedTarget.startsWith('char_');
    const id = selectedTarget;
    const name = isCharacter 
      ? players.find(p => `char_${p.character?.id}` === id)?.character?.name || 'Unknown Player'
      : monsters.find(m => m.name === id)?.name || 'Unknown Monster';

    if (combatants.find(c => c.id === id)) {
        alert(`${name} is already in the encounter.`);
        return;
    }
      
    setCombatants(prev => [...prev, { id, name, roll }].sort((a, b) => b.roll - a.roll));
    setSelectedTarget('');
    setInitiativeRoll('');
  };

  const handleStartEncounter = () => {
    if (combatants.length < 2) {
      alert('Please add at least two combatants to start the encounter.');
      return;
    }
    onSubmit(combatants);
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <header className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Setup Encounter</h2>
          <button onClick={onClose} className={styles.closeButton}>&times;</button>
        </header>

        <ul className={styles.combatantList}>
          {combatants.map((c) => (
            <li key={c.id} className={styles.combatant}>
              <span className={styles.combatantName}>{c.name}</span>
              <span className={styles.combatantRoll}>{c.roll}</span>
            </li>
          ))}
          {combatants.length === 0 && <p>Add creatures to the encounter.</p>}
        </ul>

        <div className={styles.dmForm}>
          <h3>Add Combatant</h3>
          <form onSubmit={handleAddCombatant} className={styles.addCombatantFields}>
            <select value={selectedTarget} onChange={e => setSelectedTarget(e.target.value)} required>
              <option value="">-- Select Creature --</option>
              <optgroup label="Players">
                {players.filter(p => p.character).map(p => (
                  <option key={p.character!.id} value={`char_${p.character!.id}`}>{p.character!.name}</option>
                ))}
              </optgroup>
              <optgroup label="Monsters">
                {monsters.map(m => (
                  <option key={m.id} value={m.name}>{m.name}</option>
                ))}
              </optgroup>
            </select>
            <input 
              type="number" 
              placeholder="Roll" 
              value={initiativeRoll} 
              onChange={e => setInitiativeRoll(e.target.value)}
              required 
            />
            <ThemedButton type="submit">Add</ThemedButton>
          </form>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <ThemedButton onClick={handleStartEncounter} variant="green" shape="pill">
            Start Encounter
          </ThemedButton>
        </div>
      </div>
    </div>
  );
};

export default EncounterModal;
