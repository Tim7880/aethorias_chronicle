// Path: src/components/common/ThemedButton.tsx
import React from 'react';
import styles from './ThemedButton.module.css'; // Import CSS Modules

interface ThemedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode; // Usually for text, but our button is a rune
  runeSymbol?: string;        // To pass the rune character, e.g., "❖"
  variant?: 'red' | 'green';  // For different wax seal colors
  tooltipText?: string;       // For the hover tooltip
  // Add any other specific props you might need, like 'isLoading', 'size', etc.
}

const ThemedButton: React.FC<ThemedButtonProps> = ({
  children,
  runeSymbol = "❖", // Default rune symbol
  variant = 'red',    // Default wax seal color
  tooltipText,
  className,        // To allow passing additional custom classes
  ...props          // Spread other native button props like onClick, type, disabled
}) => {
  const buttonClasses = [
    styles.themedButton,
    styles.waxSeal,
    variant === 'red' ? styles.redSeal : styles.greenSeal,
    className || ''
  ].join(' ').trim();

  return (
    <button className={buttonClasses} {...props}>
      <span className={styles.runeSymbol}>{runeSymbol}</span>
      {tooltipText && <span className={styles.tooltipText}>{tooltipText}</span>}
      {/* If you want text alongside the rune, you could use children here */}
      {/* {children && <span className={styles.buttonText}>{children}</span>} */}
    </button>
  );
};

export default ThemedButton;