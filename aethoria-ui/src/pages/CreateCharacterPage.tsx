// Path: src/pages/CreateCharacterPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ThemedInput from '../components/common/ThemedInput';
import ThemedButton from '../components/common/ThemedButton';
import { characterService} from '../services/characterService'; 
import type { CharacterCreatePayload as CharacterCreatePayloadType } from '../services/characterService'; // Use type-only import for payload
import { useAuth } from '../contexts/AuthContext';

// --- Options for Dropdowns ---
const RACES = [
  "Human", "Elf (High)", "Elf (Wood)", "Elf (Drow)", 
  "Dwarf (Hill)", "Dwarf (Mountain)", 
  "Halfling (Lightfoot)", "Halfling (Stout)",
  "Dragonborn", "Gnome (Rock)", "Gnome (Forest)",
  "Half-Elf", "Half-Orc", "Tiefling"
];

const CLASSES = [
  "Barbarian", "Bard", "Cleric", "Druid", 
  "Fighter", "Monk", "Paladin", "Ranger", 
  "Rogue", "Sorcerer", "Warlock", "Wizard",
  // "Artificer" // SRD does not include Artificer, add if you plan to support
];

const ALIGNMENTS = [
  "Lawful Good", "Neutral Good", "Chaotic Good",
  "Lawful Neutral", "True Neutral", "Chaotic Neutral",
  "Lawful Evil", "Neutral Evil", "Chaotic Evil"
];
// --- End Options ---

interface CharacterFormState {
  name: string;
  race: string; // Will hold the selected race
  character_class: string; // Will hold the selected class
  alignment: string; // Will hold the selected alignment
  background_story: string;
  appearance_description: string;
  strength: string;
  dexterity: string;
  constitution: string;
  intelligence: string;
  wisdom: string;
  charisma: string;
  chosen_cantrip_ids_str: string;
  chosen_initial_spell_ids_str: string;
}

const CreateCharacterPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate(); 

  const [formData, setFormData] = useState<CharacterFormState>({
    name: '',
    race: RACES[0] || '', // Default to the first race or empty
    character_class: CLASSES[0] || '', // Default to the first class or empty
    alignment: ALIGNMENTS[0] || '', // Default to the first alignment or empty
    background_story: '',
    appearance_description: '',
    strength: '10',
    dexterity: '10',
    constitution: '10',
    intelligence: '10',
    wisdom: '10',
    charisma: '10',
    chosen_cantrip_ids_str: '',
    chosen_initial_spell_ids_str: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (
    // Now also handles HTMLSelectElement
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> 
  ) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const parseIdList = (str: string): number[] | null => {
    if (!str.trim()) return null;
    return str.split(',').map(id => parseInt(id.trim(), 10)).filter(id => !isNaN(id));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!auth?.token) {
      setError("You must be logged in to create a character.");
      return;
    }
    setIsLoading(true);
    setError(null);

    const payload: CharacterCreatePayloadType = { // Use the imported type
      name: formData.name,
      race: formData.race || null,
      character_class: formData.character_class || null,
      alignment: formData.alignment || null,
      background_story: formData.background_story || null,
      appearance_description: formData.appearance_description || null,
      strength: parseInt(formData.strength, 10) || undefined,
      dexterity: parseInt(formData.dexterity, 10) || undefined,
      constitution: parseInt(formData.constitution, 10) || undefined,
      intelligence: parseInt(formData.intelligence, 10) || undefined,
      wisdom: parseInt(formData.wisdom, 10) || undefined,
      charisma: parseInt(formData.charisma, 10) || undefined,
      chosen_cantrip_ids: parseIdList(formData.chosen_cantrip_ids_str),
      chosen_initial_spell_ids: parseIdList(formData.chosen_initial_spell_ids_str),
    };

    for (const key in payload) {
        if (payload[key as keyof CharacterCreatePayloadType] === undefined) {
            delete payload[key as keyof CharacterCreatePayloadType];
        }
    }

    console.log('Submitting character creation payload:', payload);

    try {
      const newCharacter = await characterService.createCharacter(auth.token, payload);
      console.log("Character created successfully:", newCharacter);
      alert(`Character "${newCharacter.name}" created successfully!`);
      navigate(`/dashboard`); 
    } catch (err: any) {
      console.error('Character creation failed:', err);
      setError(err.message || "Failed to create character. Please check your inputs.");
    } finally {
      setIsLoading(false);
    }
  };

  const pageStyle: React.CSSProperties = { /* ... same as before ... */ 
    padding: '20px', maxWidth: '800px', margin: '20px auto',
  };
  const formContainerStyle: React.CSSProperties = { /* ... same as before ... */
    backgroundColor: 'var(--parchment-highlight)', padding: '30px 40px',
    borderRadius: '8px', boxShadow: '0px 6px 18px rgba(0,0,0,0.15), 0px 0px 0px 1px var(--ink-color-light)',
    border: '1px solid rgba(120, 90, 70, 0.3)',
  };
  const titleStyle: React.CSSProperties = { /* ... same as before ... */
    fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)',
    fontSize: '2.8em', marginBottom: '1em', textAlign: 'center',
  };
  const errorStyle: React.CSSProperties = { /* ... same as before ... */
    fontFamily: 'var(--font-body-primary)', color: '#a02c2c',
    marginTop: '1em', minHeight: '1.2em', textAlign: 'center',
  };
  const abilityScoreGridStyle: React.CSSProperties = { /* ... same as before ... */
    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '1.5em', marginBottom: '1.5em'
  };
  const formGroupStyle: React.CSSProperties = { /* ... same as before ... */
    marginBottom: '1.2em', display: 'flex', flexDirection: 'column',
  };
  const labelStyle: React.CSSProperties = { /* ... same as before ... */
    display: 'block', fontFamily: 'var(--font-script-annotation)', fontSize: '1.1em', 
    color: 'var(--ink-color-medium)', marginBottom: '0.4em', textAlign: 'left',
  };
  // Style for <select> elements to mimic ThemedInput
  const selectStyle: React.CSSProperties = { 
    fontFamily: 'var(--font-body-primary)', // Using body font for select options for readability
    fontSize: '1.2em', // Adjust as needed
    color: 'var(--ink-color-dark)',
    backgroundColor: 'rgba(245, 235, 215, 0.4)',
    border: '1px solid rgba(220, 210, 190, 0.7)',
    padding: '0.6em 0.9em',
    borderRadius: '3px',
    boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)',
    width: '100%',
    boxSizing: 'border-box',
    cursor: 'pointer',
  };
  const textAreaStyle: React.CSSProperties = { /* ... same as before ... */ 
    fontFamily: 'var(--font-handwritten-input)', fontSize: '1.5em', color: 'var(--ink-color-dark)',
    backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)',
    padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)',
    width: '100%', boxSizing: 'border-box', minHeight: '100px',
  };


  return (
    <div style={pageStyle}>
      <div style={formContainerStyle}>
        <h1 style={titleStyle}>Chronicle a New Adventurer</h1>
        <form onSubmit={handleSubmit}>
          <ThemedInput label="Character Name:" id="name" name="name" type="text" value={formData.name} onChange={handleChange} placeholder="e.g., Eldrin Moonwhisper" disabled={isLoading} required />

          {/* --- MODIFIED Race, Class, Alignment to Dropdowns --- */}
          <div style={{display: 'flex', gap: '1.5em', flexWrap: 'wrap', marginTop: '1.2em' }}>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle /* Apply form group style */}}>
              <label htmlFor="race" style={labelStyle}>Race:</label>
              <select id="race" name="race" value={formData.race} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                <option value="">-- Select Race --</option>
                {RACES.map(race => <option key={race} value={race}>{race}</option>)}
              </select>
            </div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}>
              <label htmlFor="character_class" style={labelStyle}>Class:</label>
              <select id="character_class" name="character_class" value={formData.character_class} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                <option value="">-- Select Class --</option>
                {CLASSES.map(cls => <option key={cls} value={cls}>{cls}</option>)}
              </select>
            </div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}>
              <label htmlFor="alignment" style={labelStyle}>Alignment:</label>
              <select id="alignment" name="alignment" value={formData.alignment} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                <option value="">-- Select Alignment --</option>
                {ALIGNMENTS.map(align => <option key={align} value={align}>{align}</option>)}
              </select>
            </div>
          </div>
          {/* --- END MODIFIED --- */}

          <h2 style={{fontFamily: 'var(--font-script-annotation)', fontSize: '1.5em', color: 'var(--ink-color-medium)', marginTop: '1.5em', marginBottom: '0.8em'}}>Ability Scores</h2>
          <div style={abilityScoreGridStyle}>
            {(['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const).map((stat) => (
              <ThemedInput key={stat} label={`${stat.charAt(0).toUpperCase() + stat.slice(1)}:`} id={stat} name={stat} type="number" value={formData[stat as keyof CharacterFormState]} onChange={handleChange} min="1" max="30" disabled={isLoading} />
            ))}
          </div>

          <div style={formGroupStyle}><label htmlFor="background_story" style={labelStyle}>Background Story:</label><textarea id="background_story" name="background_story" value={formData.background_story} onChange={handleChange} placeholder="Their history..." disabled={isLoading} style={textAreaStyle} rows={4}/></div>
          <div style={formGroupStyle}><label htmlFor="appearance_description" style={labelStyle}>Appearance Description:</label><textarea id="appearance_description" name="appearance_description" value={formData.appearance_description} onChange={handleChange} placeholder="What do they look like?" disabled={isLoading} style={textAreaStyle} rows={3}/></div>

          {formData.character_class && formData.character_class.toLowerCase() === 'sorcerer' && (
            <>
              <ThemedInput label="Chosen Cantrip IDs (L1 Sorcerer - comma-separated, e.g., 1,2,3,4):" id="chosen_cantrip_ids_str" name="chosen_cantrip_ids_str" type="text" value={formData.chosen_cantrip_ids_str} onChange={handleChange} placeholder="Enter 4 cantrip IDs" disabled={isLoading} />
              <ThemedInput label="Chosen Initial L1 Spell IDs (L1 Sorcerer - comma-separated, e.g., 5,6):" id="chosen_initial_spell_ids_str" name="chosen_initial_spell_ids_str" type="text" value={formData.chosen_initial_spell_ids_str} onChange={handleChange} placeholder="Enter 2 level 1 spell IDs" disabled={isLoading} />
            </>
          )}

          {error && <p style={errorStyle}>{error}</p>}
          <div style={{ marginTop: '2.5em', textAlign: 'center' }}>
            <ThemedButton type="submit" runeSymbol="✨" variant="green" tooltipText={isLoading ? "Chronicling..." : "Begin Their Chronicle"} aria-label="Create Character" disabled={isLoading}>
              {isLoading ? "Saving..." : ""}
            </ThemedButton>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCharacterPage;
