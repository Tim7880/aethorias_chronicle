// Path: src/pages/RacesViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { Race } from '../types/race';
import styles from './RacesViewPage.module.css';

const RacesViewPage: React.FC = () => {
  const auth = useAuth();
  const [races, setRaces] = useState<Race[]>([]);
  const [selectedRace, setSelectedRace] = useState<Race | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRaces = async () => {
      if (auth.token) {
        setIsLoading(true);
        setError(null);
        try {
          const raceData = await gameDataService.getRaces(auth.token);
          setRaces(raceData.sort((a, b) => a.name.localeCompare(b.name)));
        } catch (err: any) {
          setError(err.message || "Failed to load race data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadRaces();
  }, [auth.token]);

  const handleRaceSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedRaceName = e.target.value;
    const raceDetails = races.find(r => r.name === selectedRaceName) || null;
    setSelectedRace(raceDetails);
  };

  const formatAbilityScores = (scores: { [key: string]: number }) => {
    return Object.entries(scores)
      .map(([ability, value]) => `${ability.charAt(0).toUpperCase() + ability.slice(1)} +${value}`)
      .join(', ');
  };

  if (isLoading) {
    return <div className={styles.pageContainer}><p>Loading racial archives...</p></div>;
  }

  if (error) {
    return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;
  }

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.title}>Races of Aethoria</h1>
      </header>

      <div className={styles.selectorContainer}>
        <label htmlFor="race-selector" className={styles.selectorLabel}>Choose a Race to View</label>
        <select 
          id="race-selector" 
          onChange={handleRaceSelection} 
          className={styles.raceSelector}
          defaultValue=""
        >
          <option value="" disabled>-- Select a Race --</option>
          {races.map(race => (
            <option key={race.id} value={race.name}>
              {race.name}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.raceDisplay}>
        {selectedRace ? (
          <div>
            <h2 className={styles.raceName}>{selectedRace.name}</h2>
            <p className={styles.raceDescription}>{selectedRace.description || "No description available."}</p>
            
            <div className={styles.raceDetailsGrid}>
                <div className={styles.detailItem}><strong>Ability Scores:</strong> {formatAbilityScores(selectedRace.ability_score_increase)}</div>
                <div className={styles.detailItem}><strong>Size:</strong> {selectedRace.size}</div>
                <div className={styles.detailItem}><strong>Speed:</strong> {selectedRace.speed} ft.</div>
                <div className={styles.detailItem}><strong>Languages:</strong> {selectedRace.languages}</div>
            </div>

            {selectedRace.racial_traits && selectedRace.racial_traits.length > 0 && (
                <div>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)'}}>Racial Traits</h3>
                    <ul className={styles.traitsList}>
                        {selectedRace.racial_traits.map(trait => (
                            <li key={trait.name} className={styles.traitItem}>
                                <div className={styles.traitName}>{trait.name}</div>
                                <p className={styles.traitDesc}>{trait.desc}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* --- NEW: Subrace Display Section --- */}
            {selectedRace.subraces && selectedRace.subraces.length > 0 && (
                <div className={styles.subraceContainer}>
                    <h3 style={{fontFamily: 'var(--font-heading-ornate)'}}>Subraces</h3>
                    {selectedRace.subraces.map(subrace => (
                        <div key={subrace.name} className={styles.subraceBox}>
                            <h4 className={styles.subraceTitle}>{subrace.name}</h4>
                            <p className={styles.subraceASI}><strong>Ability Score Increase:</strong> {formatAbilityScores(subrace.ability_score_increase)}</p>
                            {subrace.racial_traits && subrace.racial_traits.map(trait => (
                                <div key={trait.name} className={styles.traitItem}>
                                    <div className={styles.traitName}>{trait.name}</div>
                                    <p className={styles.traitDesc}>{trait.desc}</p>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            )}
            {/* --- END NEW --- */}

          </div>
        ) : (
          <p className={styles.promptText}>Select a race from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default RacesViewPage;


