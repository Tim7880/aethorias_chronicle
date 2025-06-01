// Path: src/components/common/ThemedInput.tsx
import React from 'react'; // React itself is used for JSX
import type { InputHTMLAttributes } from 'react'; // Use 'import type' for the type
import styles from './ThemedInput.module.css'; // Import CSS Modules

interface ThemedInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  id: string; // Ensure id is always provided for label association
  // Add any other specific props you might need
}

const ThemedInput: React.FC<ThemedInputProps> = ({
  label,
  id,
  className, // To allow passing additional custom classes
  type = "text", // Default input type
  ...props       // Spread other native input props like value, onChange, name, placeholder etc.
}) => {
  const inputClasses = [
    styles.themedInput,
    styles.parchmentIndentation, // Class for the specific style
    className || ''
  ].join(' ').trim();

  return (
    <div className={styles.inputGroup}>
      {label && <label htmlFor={id} className={styles.inputLabel}>{label}</label>}
      <input
        type={type}
        id={id}
        className={inputClasses}
        {...props}
      />
    </div>
  );
};

export default ThemedInput;