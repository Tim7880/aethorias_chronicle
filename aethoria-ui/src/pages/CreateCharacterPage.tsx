// Path: src/pages/CreateCharacterPage.tsx
import React, { useState, useEffect } from 'react'; // Removed useCallback, may add useCallback later if needed
import { useNavigate } from 'react-router-dom';
import ThemedInput from '../components/common/ThemedInput';
import ThemedButton from '../components/common/ThemedButton';
import { characterService } from '../services/characterService'; 
import type { CharacterCreatePayload } from '../services/characterService';
import { spellService } from '../services/spellService'; 
import type { SpellDefinition } from '../types/spell'; 
import { useAuth } from '../contexts/AuthContext';

const RACES = [
    "Human", "Elf (High)", "Elf (Wood)", "Elf (Drow)", "Dwarf (Hill)", "Dwarf (Mountain)", 
    "Halfling (Lightfoot)", "Halfling (Stout)", "Dragonborn", "Gnome (Rock)", "Gnome (Forest)",
    "Half-Elf", "Half-Orc", "Tiefling"
];
const CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", 
    "Rogue", "Sorcerer", "Warlock", "Wizard"
];
const ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil"
];
const SORCERER_L1_CANTRIPS_COUNT = 4;
const SORCERER_L1_SPELLS_COUNT = 2;

interface CharacterFormState {
  name: string;
  race: string;
  character_class: string;
  alignment: string;
  background_story: string;
  appearance_description: string;
  strength: string;
  dexterity: string;
  constitution: string;
  intelligence: string;
  wisdom: string;
  charisma: string;
  chosen_cantrip_ids: (number | string)[]; 
  chosen_initial_spell_ids: (number | string)[];
}

const CreateCharacterPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate(); 

  const [formData, setFormData] = useState<CharacterFormState>({
    name: '',
    race: RACES[0] || '', 
    character_class: CLASSES[0] || '', 
    alignment: ALIGNMENTS[0] || '', 
    background_story: '',
    appearance_description: '',
    strength: '10',
    dexterity: '10',
    constitution: '10',
    intelligence: '10',
    wisdom: '10',
    charisma: '10',
    chosen_cantrip_ids: Array(SORCERER_L1_CANTRIPS_COUNT).fill(''),
    chosen_initial_spell_ids: Array(SORCERER_L1_SPELLS_COUNT).fill(''),
  });

  const [availableCantrips, setAvailableCantrips] = useState<SpellDefinition[]>([]);
  const [availableL1Spells, setAvailableL1Spells] = useState<SpellDefinition[]>([]);
  const [isLoadingSpells, setIsLoadingSpells] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchSpellsForClass = async () => {
      if (auth?.token && formData.character_class.toLowerCase() === 'sorcerer') {
        setIsLoadingSpells(true);
        try {
          const allSpells = await spellService.getSpells(auth.token);
          const sorcererCantrips = allSpells.filter(spell => 
            spell.level === 0 && 
            spell.dnd_classes && 
            spell.dnd_classes.map(c => c.toLowerCase()).includes('sorcerer')
          );
          const sorcererL1Spells = allSpells.filter(spell => 
            spell.level === 1 && 
            spell.dnd_classes && 
            spell.dnd_classes.map(c => c.toLowerCase()).includes('sorcerer')
          );
          setAvailableCantrips(sorcererCantrips);
          setAvailableL1Spells(sorcererL1Spells);
        } catch (err) {
          console.error("Failed to fetch spells for Sorcerer:", err);
          setError("Could not load available spells for Sorcerer.");
        } finally {
          setIsLoadingSpells(false);
        }
      } else {
        setAvailableCantrips([]);
        setAvailableL1Spells([]);
      }
    };
    fetchSpellsForClass();
  }, [formData.character_class, auth?.token]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> 
  ) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };
  
  const handleSpellSelectionChange = (
    e: React.ChangeEvent<HTMLSelectElement>, 
    index: number, 
    type: 'cantrip' | 'spell'
  ) => {
    const spellId = e.target.value ? parseInt(e.target.value, 10) : '';
    setFormData(prevData => {
      const updatedSpellIds = type === 'cantrip' 
        ? [...prevData.chosen_cantrip_ids] 
        : [...prevData.chosen_initial_spell_ids];
      updatedSpellIds[index] = spellId;
      return {
        ...prevData,
        [type === 'cantrip' ? 'chosen_cantrip_ids' : 'chosen_initial_spell_ids']: updatedSpellIds
      };
    });
  };

  const parseIdList = (ids: (string | number)[]): number[] | null => {
    const num_ids = ids
        .map(id => typeof id === 'string' ? parseInt(id.trim(), 10) : id)
        .filter(id => typeof id === 'number' && !isNaN(id) && id !== 0); // Ensure it's a number and not 0 (if "" was an option)
    return num_ids.length > 0 ? num_ids : null;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!auth?.token) {
      setError("You must be logged in to create a character.");
      return;
    }
    setIsLoading(true);
    setError(null);

    const cantripIds = parseIdList(formData.chosen_cantrip_ids);
    const initialSpellIds = parseIdList(formData.chosen_initial_spell_ids);

    if (formData.character_class.toLowerCase() === 'sorcerer') {
        if ((cantripIds?.length || 0) !== SORCERER_L1_CANTRIPS_COUNT) {
            setError(`Please select exactly ${SORCERER_L1_CANTRIPS_COUNT} unique cantrips.`);
            setIsLoading(false);
            return;
        }
        if ((initialSpellIds?.length || 0) !== SORCERER_L1_SPELLS_COUNT) {
            setError(`Please select exactly ${SORCERER_L1_SPELLS_COUNT} unique level 1 spells.`);
            setIsLoading(false);
            return;
        }
        const allChosenIds = [...(cantripIds || []), ...(initialSpellIds || [])];
        if (new Set(allChosenIds).size !== allChosenIds.length) {
            setError("Cannot select the same spell as both a cantrip and a leveled spell, or duplicate choices.");
            setIsLoading(false);
            return;
        }
    }

    const parseStat = (val: string): number | undefined => { 
        const num = parseInt(val, 10); 
        return isNaN(num) ? undefined : num; 
    };

    const payload: CharacterCreatePayload = {
      name: formData.name,
      race: formData.race || undefined,
      character_class: formData.character_class || undefined,
      alignment: formData.alignment || undefined,
      background_story: formData.background_story || undefined,
      appearance_description: formData.appearance_description || undefined,
      strength: parseStat(formData.strength),
      dexterity: parseStat(formData.dexterity),
      constitution: parseStat(formData.constitution),
      intelligence: parseStat(formData.intelligence),
      wisdom: parseStat(formData.wisdom),
      charisma: parseStat(formData.charisma),
      chosen_cantrip_ids: formData.character_class.toLowerCase() === 'sorcerer' ? cantripIds : null,
      chosen_initial_spell_ids: formData.character_class.toLowerCase() === 'sorcerer' ? initialSpellIds : null,
    };
    
    for (const key in payload) {
        if (payload[key as keyof CharacterCreatePayload] === undefined) {
            delete payload[key as keyof CharacterCreatePayload];
        }
    }
            
    console.log('Submitting character creation payload:', JSON.stringify(payload, null, 2));

    try {
      const newCharacter = await characterService.createCharacter(auth.token, payload);
      console.log("Character created successfully:", newCharacter);
      alert(`Character "${newCharacter.name}" (ID: ${newCharacter.id}) created successfully!`);
      navigate(`/dashboard`); 
    } catch (err: any) {
      console.error('Character creation failed:', err);
      setError(err.message || "Failed to create character. Please check your inputs and try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  // --- Styling (pageStyle, formContainerStyle, etc. as before) ---
  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '800px', margin: '20px auto',};
  const formContainerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px 40px', borderRadius: '8px', boxShadow: '0px 6px 18px rgba(0,0,0,0.15), 0px 0px 0px 1px var(--ink-color-light)', border: '1px solid rgba(120, 90, 70, 0.3)',};
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', fontSize: '2.8em', marginBottom: '1em', textAlign: 'center',};
  const errorStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', color: '#a02c2c', marginTop: '1em', minHeight: '1.2em', textAlign: 'center',};
  const abilityScoreGridStyle: React.CSSProperties = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5em', marginBottom: '1.5em'};
  const formGroupStyle: React.CSSProperties = { marginBottom: '1.2em', display: 'flex', flexDirection: 'column',};
  const labelStyle: React.CSSProperties = { display: 'block', fontFamily: 'var(--font-script-annotation)', fontSize: '1.1em', color: 'var(--ink-color-medium)', marginBottom: '0.4em', textAlign: 'left',};
  const selectStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', fontSize: '1.2em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', cursor: 'pointer',};
  const textAreaStyle: React.CSSProperties = { fontFamily: 'var(--font-handwritten-input)', fontSize: '1.5em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', minHeight: '100px',};

  return (
    <div style={pageStyle}>
      <div style={formContainerStyle}>
        <h1 style={titleStyle}>Chronicle a New Adventurer</h1>
        <form onSubmit={handleSubmit}>
          <ThemedInput label="Character Name:" id="name" name="name" type="text" value={formData.name} onChange={handleChange} placeholder="e.g., Eldrin Moonwhisper" disabled={isLoading} required />
          <div style={{display: 'flex', gap: '1.5em', flexWrap: 'wrap', marginTop: '1.2em' }}>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}><label htmlFor="race" style={labelStyle}>Race:</label><select id="race" name="race" value={formData.race} onChange={handleChange} disabled={isLoading} style={selectStyle} required><option value="">-- Select Race --</option>{RACES.map(race => <option key={race} value={race}>{race}</option>)}</select></div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}><label htmlFor="character_class" style={labelStyle}>Class:</label><select id="character_class" name="character_class" value={formData.character_class} onChange={handleChange} disabled={isLoading} style={selectStyle} required><option value="">-- Select Class --</option>{CLASSES.map(cls => <option key={cls} value={cls}>{cls}</option>)}</select></div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}><label htmlFor="alignment" style={labelStyle}>Alignment:</label><select id="alignment" name="alignment" value={formData.alignment} onChange={handleChange} disabled={isLoading} style={selectStyle} required><option value="">-- Select Alignment --</option>{ALIGNMENTS.map(align => <option key={align} value={align}>{align}</option>)}</select></div>
          </div>
          <h2 style={{fontFamily: 'var(--font-script-annotation)', fontSize: '1.5em', color: 'var(--ink-color-medium)', marginTop: '1.5em', marginBottom: '0.8em'}}>Ability Scores</h2>
          <div style={abilityScoreGridStyle}>
            {(['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const).map((stat) => (
              <ThemedInput 
                key={stat} 
                label={`${stat.charAt(0).toUpperCase() + stat.slice(1)}:`} 
                id={stat} 
                name={stat} 
                type="number" 
                value={formData[stat]} // <--- REMOVED 'as keyof CharacterFormState'
                onChange={handleChange} 
                min="1" 
                max="30" // Or make this dynamic based on tier if ever needed here
                disabled={isLoading} 
              />
            ))}
          </div>
          
          <div style={formGroupStyle}><label htmlFor="background_story" style={labelStyle}>Background Story:</label><textarea id="background_story" name="background_story" value={formData.background_story} onChange={handleChange} placeholder="Their history..." disabled={isLoading} style={textAreaStyle} rows={4}/></div>
          <div style={formGroupStyle}><label htmlFor="appearance_description" style={labelStyle}>Appearance Description:</label><textarea id="appearance_description" name="appearance_description" value={formData.appearance_description} onChange={handleChange} placeholder="What do they look like?" disabled={isLoading} style={textAreaStyle} rows={3}/></div>
          
          {formData.character_class && formData.character_class.toLowerCase() === 'sorcerer' && (
            <div style={{marginTop: '1.5em'}}>
              <h3 style={{fontFamily: 'var(--font-script-annotation)', fontSize: '1.3em', color: 'var(--ink-color-medium)', marginBottom: '0.8em'}}>
                Initial Spells & Cantrips (Level 1 Sorcerer)
              </h3>
              {isLoadingSpells && <p>Loading spells...</p>}
              
              <div style={{marginBottom: '1em'}}>
                <p style={labelStyle}>Choose {SORCERER_L1_CANTRIPS_COUNT} Cantrips:</p>
                {Array.from({ length: SORCERER_L1_CANTRIPS_COUNT }).map((_, index) => (
                  <div key={`cantrip-select-${index}`} style={formGroupStyle}>
                    <select 
                      name={`chosen_cantrip_ids[${index}]`} // This name might not map directly to formData state
                      value={formData.chosen_cantrip_ids[index] || ""}
                      onChange={(e) => handleSpellSelectionChange(e, index, 'cantrip')}
                      style={selectStyle}
                      disabled={isLoading || isLoadingSpells}
                      required
                    >
                      <option value="">-- Select Cantrip {index + 1} --</option>
                      {availableCantrips.map(spell => (
                        <option key={spell.id} value={spell.id}>{spell.name} (L0)</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>

              <div>
                <p style={labelStyle}>Choose {SORCERER_L1_SPELLS_COUNT} Level 1 Spells:</p>
                {Array.from({ length: SORCERER_L1_SPELLS_COUNT }).map((_, index) => (
                  <div key={`spell-select-${index}`} style={formGroupStyle}>
                    <select 
                      name={`chosen_initial_spell_ids[${index}]`} // This name might not map directly
                      value={formData.chosen_initial_spell_ids[index] || ""}
                      onChange={(e) => handleSpellSelectionChange(e, index, 'spell')}
                      style={selectStyle}
                      disabled={isLoading || isLoadingSpells}
                      required
                    >
                      <option value="">-- Select Level 1 Spell {index + 1} --</option>
                      {availableL1Spells.map(spell => (
                        <option key={spell.id} value={spell.id}>{spell.name} (L{spell.level})</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {error && <p style={errorStyle}>{error}</p>}
          <div style={{ marginTop: '2.5em', textAlign: 'center' }}>
            <ThemedButton 
              type="submit" 
              runeSymbol="✨" 
              variant="green" 
              tooltipText={isLoading ? "Chronicling..." : "Begin Their Chronicle"}
              aria-label="Create Character"
              disabled={isLoading}
            >
              {isLoading ? "Saving..." : ""}
            </ThemedButton>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCharacterPage;
