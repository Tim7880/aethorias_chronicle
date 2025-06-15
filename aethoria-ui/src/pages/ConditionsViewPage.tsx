// Path: src/pages/ConditionsViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { Condition } from '../types/condition';
import styles from './ConditionsViewPage.module.css';

const ConditionsViewPage: React.FC = () => {
  const auth = useAuth();
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [selectedCondition, setSelectedCondition] = useState<Condition | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getConditions(auth.token);
          setConditions(data.sort((a, b) => a.name.localeCompare(b.name)));
        } catch (err: any) {
          setError(err.message || "Failed to load condition data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadData();
  }, [auth.token]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = conditions.find(c => c.name === selectedName) || null;
    setSelectedCondition(details);
  };

  if (isLoading) return <div className={styles.pageContainer}><p>Loading conditions...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.selectorContainer}>
        <label htmlFor="condition-selector" className={styles.selectorLabel}>Browse Conditions</label>
        <select id="condition-selector" onChange={handleSelection} className={styles.conditionSelector} defaultValue="">
          <option value="" disabled>-- Select a Condition --</option>
          {conditions.map(condition => (
            <option key={condition.id} value={condition.name}>{condition.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.conditionDisplay}>
        {selectedCondition ? (
          <div>
            <h2 className={styles.conditionName}>{selectedCondition.name}</h2>
            <div className={styles.conditionDescription}>
              {selectedCondition.description.split('\n').map((line, index) => (
                <p key={index}>{line.replace(/^- /, '')}</p>
              ))}
            </div>
          </div>
        ) : (
          <p className={styles.promptText}>Select a condition from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default ConditionsViewPage;
