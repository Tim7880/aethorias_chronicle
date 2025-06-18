// Path: src/components/game/InitiativeTracker.tsx
import React from 'react';
import type { InitiativeEntry } from '../../types/campaign';
import styles from './InitiativeTracker.module.css';

interface InitiativeTrackerProps {
  entries: InitiativeEntry[];
  activeEntryId?: number | null;
}

const InitiativeTracker: React.FC<InitiativeTrackerProps> = ({ entries, activeEntryId }) => {
  if (entries.length === 0) {
    return <p>No one is in the initiative order.</p>;
  }

  return (
    <ul className={styles.initiativeList}>
      {entries.map(entry => (
        <li 
          key={entry.id} 
          className={`${styles.entry} ${entry.id === activeEntryId ? styles.active : ''}`}
        >
          <span className={styles.name}>
            {entry.character ? entry.character.name : entry.monster_name}
          </span>
          <span className={styles.roll}>{entry.initiative_roll}</span>
        </li>
      ))}
    </ul>
  );
};

export default InitiativeTracker;
