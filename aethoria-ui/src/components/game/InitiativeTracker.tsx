// Path: src/components/game/InitiativeTracker.tsx
import React from 'react';
import type { InitiativeEntry } from '../../types/campaign'; // Assuming this type is defined correctly
import styles from './InitiativeTracker.module.css';

interface InitiativeTrackerProps {
  entries: InitiativeEntry[];
  activeEntryId?: number | string | null;
}

const InitiativeTracker: React.FC<InitiativeTrackerProps> = ({ entries, activeEntryId }) => {
  if (!entries || entries.length === 0) {
    return <p style={{ textAlign: 'center', fontStyle: 'italic', color: '#72767d' }}>Combat has not started.</p>;
  }

  // The list is already sorted by the backend.
  return (
    <ul className={styles.initiativeList}>
      {entries.map((entry: any) => ( // Using 'any' temporarily to match in-memory state
        <li 
          key={entry.id} 
          className={`${styles.entry} ${entry.id === activeEntryId ? styles.active : ''}`}
        >
          <span className={styles.name}>{entry.name}</span>
          <span className={styles.roll}>{entry.roll}</span>
        </li>
      ))}
    </ul>
  );
};

export default InitiativeTracker;

