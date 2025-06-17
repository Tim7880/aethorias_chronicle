// Path: src/components/game/DiceRoller.tsx
import React, { useState } from 'react';
import ThemedButton from '../common/ThemedButton';
import styles from './DiceRoller.module.css';

const DICE_TYPES = [4, 6, 8, 10, 12, 20, 100];

interface DiceRollerProps {
  onRoll: (sides: number, count: number) => void;
  disabled?: boolean;
}

const DiceRoller: React.FC<DiceRollerProps> = ({ onRoll, disabled = false }) => {
  const [count, setCount] = useState(1);

  const handleCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    // Allow a reasonable number of dice, e.g., 1 to 100
    if (value > 0 && value <= 100) {
      setCount(value);
    }
  };

  const handleRollClick = (sides: number) => {
    onRoll(sides, count);
  };

  return (
    <div>
      <div className={styles.countContainer}>
        <label htmlFor="dice-count" className={styles.countLabel}>Count:</label>
        <input
          id="dice-count"
          type="number"
          value={count}
          onChange={handleCountChange}
          className={styles.countInput}
          min="1"
          max="100"
          disabled={disabled}
        />
      </div>
      <div className={styles.diceRollerContainer}>
        {DICE_TYPES.map(sides => (
          <ThemedButton 
            key={`d${sides}`} 
            onClick={() => handleRollClick(sides)}
            className={styles.diceButton}
            disabled={disabled}
            shape="pill"
          >
            d{sides}
          </ThemedButton>
        ))}
      </div>
    </div>
  );
};

export default DiceRoller;
