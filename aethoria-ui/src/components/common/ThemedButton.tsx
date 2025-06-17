// Path: src/components/common/ThemedButton.tsx
import React from 'react';
import styles from './ThemedButton.module.css';

interface ThemedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode;
  runeSymbol?: string;
  variant?: 'red' | 'green';
  tooltipText?: string;
  shape?: 'round' | 'pill'; // NEW: Prop to control the shape
}

const ThemedButton: React.FC<ThemedButtonProps> = ({
  children,
  runeSymbol,
  variant = 'red',
  tooltipText,
  shape = 'pill', // Default to pill shape for text buttons
  className,
  ...props
}) => {
  // Combine all classes based on props
  const buttonClasses = [
    styles.themedButton,
    styles.waxSeal,
    variant === 'red' ? styles.redSeal : styles.greenSeal,
    shape === 'round' ? styles.shapeRound : styles.shapePill,
    className || ''
  ].join(' ').trim();

  return (
    <button className={buttonClasses} {...props}>
      {/* If children are provided, use them as text. Otherwise, fall back to runeSymbol. */}
      {children ? (
          <span className={styles.buttonText}>{children}</span>
      ) : (
          runeSymbol && <span className={styles.runeSymbol}>{runeSymbol}</span>
      )}
      {tooltipText && <span className={styles.tooltipText}>{tooltipText}</span>}
    </button>
  );
};

export default ThemedButton;
