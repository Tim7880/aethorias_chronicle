// Path: src/pages/BackgroundsViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { Background } from '../types/background';
import styles from './BackgroundsViewPage.module.css';

const BackgroundsViewPage: React.FC = () => {
  const auth = useAuth();
  const [backgrounds, setBackgrounds] = useState<Background[]>([]);
  const [selectedBackground, setSelectedBackground] = useState<Background | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadBackgrounds = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getBackgrounds(auth.token);
          setBackgrounds(data.sort((a, b) => a.name.localeCompare(b.name)));
        } catch (err: any) {
          setError(err.message || "Failed to load background data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadBackgrounds();
  }, [auth.token]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = backgrounds.find(b => b.name === selectedName) || null;
    setSelectedBackground(details);
  };

  if (isLoading) return <div className={styles.pageContainer}><p>Searching the archives...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.selectorContainer}>
        <label htmlFor="background-selector" className={styles.selectorLabel}>Explore Backgrounds</label>
        <select id="background-selector" onChange={handleSelection} className={styles.backgroundSelector} defaultValue="">
          <option value="" disabled>-- Select a Background --</option>
          {backgrounds.map(bg => (
            <option key={bg.id} value={bg.name}>{bg.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.backgroundDisplay}>
        {selectedBackground ? (
          <div>
            <h2 className={styles.backgroundName}>{selectedBackground.name}</h2>
            <p className={styles.backgroundDescription}>{selectedBackground.description || "No description available."}</p>
            
            <ul className={styles.detailList}>
                <li className={styles.detailItem}><strong>Skill Proficiencies:</strong> {selectedBackground.skill_proficiencies.join(', ')}</li>
                {selectedBackground.tool_proficiencies && <li className={styles.detailItem}><strong>Tool Proficiencies:</strong> {selectedBackground.tool_proficiencies}</li>}
                {selectedBackground.languages && <li className={styles.detailItem}><strong>Languages:</strong> {selectedBackground.languages}</li>}
                <li className={styles.detailItem}><strong>Equipment:</strong> {selectedBackground.equipment}</li>
            </ul>

            {selectedBackground.feature && (
                <div>
                    <h3 className={styles.featureName}>{selectedBackground.feature.name}</h3>
                    <p className={styles.featureDesc}>{selectedBackground.feature.desc}</p>
                </div>
            )}
          </div>
        ) : (
          <p className={styles.promptText}>Select a background from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default BackgroundsViewPage;
