// Path: src/pages/ClassesViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { DndClass } from '../types/dndClass';
import styles from './ClassesViewPage.module.css';

const ClassesViewPage: React.FC = () => {
  const auth = useAuth();
  const [classes, setClasses] = useState<DndClass[]>([]);
  const [selectedClass, setSelectedClass] = useState<DndClass | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadClasses = async () => {
      if (auth.token) {
        setIsLoading(true);
        setError(null);
        try {
          const classData = await gameDataService.getClasses(auth.token);
          setClasses(classData);
        } catch (err: any) {
          setError(err.message || "Failed to load class data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadClasses();
  }, [auth.token]);

  const handleClassSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedClassName = e.target.value;
    const classDetails = classes.find(c => c.name === selectedClassName) || null;
    setSelectedClass(classDetails);
  };

  if (isLoading) {
    return <div className={styles.pageContainer}><p>Loading class compendium...</p></div>;
  }

  if (error) {
    return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;
  }

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.title}>Class Compendium</h1>
      </header>

      <div className={styles.selectorContainer}>
        <label htmlFor="class-selector" className={styles.selectorLabel}>Choose a Class to View</label>
        <select 
          id="class-selector" 
          onChange={handleClassSelection} 
          className={styles.classSelector}
          defaultValue=""
        >
          <option value="" disabled>-- Select a Class --</option>
          {classes.map(dndClass => (
            <option key={dndClass.id} value={dndClass.name}>
              {dndClass.name}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.classDisplay}>
        {selectedClass ? (
          <div>
            <h2 className={styles.className}>{selectedClass.name}</h2>
            <p className={styles.classDescription}>{selectedClass.description || "No description available."}</p>
            <p className={styles.classHitDie}>Hit Die: d{selectedClass.hit_die}</p>
            {/* We can add a button/link here later to view full level progression */}
          </div>
        ) : (
          <p className={styles.promptText}>Select a class from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default ClassesViewPage;
