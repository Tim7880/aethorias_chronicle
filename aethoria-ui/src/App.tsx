// Path: src/App.tsx
import './App.css'; // Keep or modify for App-specific layout if needed
import ThemedButton from './components/common/ThemedButton'; // Import your button

function App() {
  const handleClick = () => {
    alert('Rune button clicked!');
  };

  return (
    <div className="App" style={{ padding: '50px', display: 'flex', gap: '20px', alignItems: 'center' }}>
      <ThemedButton 
        onClick={handleClick} 
        runeSymbol="✔" 
        variant="green" 
        tooltipText="Confirm Action"
        aria-label="Confirm" // Good for accessibility
      />
      <ThemedButton 
        onClick={() => alert('Cancel Clicked!')} 
        runeSymbol="✖" 
        variant="red" 
        tooltipText="Cancel or Close"
        aria-label="Cancel"
      />
      <ThemedButton 
        onClick={() => alert('Save Clicked!')} 
        runeSymbol="💾" // Example: floppy disk (might not fit theme) or another rune
        tooltipText="Save Progress"
        aria-label="Save"
        disabled 
      />
       <ThemedButton 
        onClick={() => alert('Next Clicked!')} 
        runeSymbol="→" 
        variant="green" 
        tooltipText="Next Step"
        aria-label="Next"
      />
    </div>
  );
}

export default App;