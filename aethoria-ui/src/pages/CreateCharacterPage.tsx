// Path: src/pages/CreateCharacterPage.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import ThemedInput from '../components/common/ThemedInput';
import ThemedButton from '../components/common/ThemedButton';
import { characterService } from '../services/characterService'; 
import type { CharacterCreatePayload } from '../services/characterService';
import { skillService } from '../services/skillService'; 
import type { SkillDefinition } from '../types/skill';
import type { SpellDefinition } from '../types/spell';
import { useAuth } from '../contexts/AuthContext';
import { spellService } from '../services/spellService';
import { gameDataService } from '../services/gameDataService';
import type { DndClass } from '../types/dndClass';

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
const MAX_INITIAL_SKILL_PROFICIENCIES = 4;

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
  chosen_skill_proficiencies: number[]; 
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
    strength: '10', dexterity: '10', constitution: '10',
    intelligence: '10', wisdom: '10', charisma: '10',
    chosen_cantrip_ids: [],
    chosen_initial_spell_ids: [],
    chosen_skill_proficiencies: [],
  });

  const [allAvailableSkills, setAllAvailableSkills] = useState<SkillDefinition[]>([]);
  const [allSpells, setAllSpells] = useState<SpellDefinition[]>([]);
  const [allDndClasses, setAllDndClasses] = useState<DndClass[]>([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadGameData = async () => {
        if (!auth.token) return;
        try {
            const [skills, spells, dndClasses] = await Promise.all([
                skillService.getSkills(auth.token),
                spellService.getSpells(auth.token),
                gameDataService.getClasses(auth.token), // Using your existing function
            ]);
            setAllAvailableSkills(skills.sort((a, b) => a.name.localeCompare(b.name)));
            setAllSpells(spells);
            setAllDndClasses(dndClasses);
        } catch (err: any) {
            console.error("Failed to load game data:", err);
            setError("Could not load necessary game data. Please try again later.");
        } finally {
            setIsLoading(false);
        }
    };
    loadGameData();
  }, [auth.token]);

  const selectedClassData = useMemo(() => {
    return allDndClasses.find(c => c.name.toLowerCase() === formData.character_class.toLowerCase());
  }, [formData.character_class, allDndClasses]);

  const spellcastingInfo = useMemo(() => {
    if (!selectedClassData) return null;
    const level1Data = selectedClassData.levels.find(l => l.level === 1);
    return level1Data?.spellcasting || null;
  }, [selectedClassData]);

  const initialCantripsCount = useMemo(() => spellcastingInfo?.cantrips_known || 0, [spellcastingInfo]);
  const initialSpellsCount = useMemo(() => spellcastingInfo?.spells_known || 0, [spellcastingInfo]);

  const { availableCantrips, availableL1Spells } = useMemo(() => {
    if (!selectedClassData) return { availableCantrips: [], availableL1Spells: [] };
    const classNameLower = selectedClassData.name.toLowerCase();
    
    const cantrips = allSpells.filter(spell => 
      spell.level === 0 && 
      spell.dnd_classes?.map(c => c.toLowerCase()).includes(classNameLower)
    ).sort((a, b) => a.name.localeCompare(b.name));

    const l1Spells = allSpells.filter(spell => 
      spell.level === 1 && 
      spell.dnd_classes?.map(c => c.toLowerCase()).includes(classNameLower)
    ).sort((a, b) => a.name.localeCompare(b.name));

    return { availableCantrips: cantrips, availableL1Spells: l1Spells };
  }, [selectedClassData, allSpells]);

  useEffect(() => {
    setFormData(prev => ({
        ...prev,
        chosen_cantrip_ids: Array(initialCantripsCount).fill(''),
        chosen_initial_spell_ids: Array(initialSpellsCount).fill('')
    }));
  }, [initialCantripsCount, initialSpellsCount]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> 
  ) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };
  
  const handleSpellSelectionChange = (e: React.ChangeEvent<HTMLSelectElement>, index: number, type: 'cantrip' | 'spell') => {
    const spellId = e.target.value ? parseInt(e.target.value, 10) : '';
    setFormData(prevData => {
      const fieldToUpdate = type === 'cantrip' ? 'chosen_cantrip_ids' : 'chosen_initial_spell_ids';
      const updatedSpellIds = [...prevData[fieldToUpdate]];
      updatedSpellIds[index] = spellId;
      return { ...prevData, [fieldToUpdate]: updatedSpellIds };
    });
  };

  const handleSkillProficiencyToggle = (skillId: number) => {
    setFormData(prevData => {
      const currentProficiencies = prevData.chosen_skill_proficiencies;
      const isAlreadySelected = currentProficiencies.includes(skillId);
      let newProficiencies: number[];

      if (isAlreadySelected) {
        newProficiencies = currentProficiencies.filter(id => id !== skillId);
      } else {
        if (currentProficiencies.length < MAX_INITIAL_SKILL_PROFICIENCIES) {
          newProficiencies = [...currentProficiencies, skillId];
        } else {
          alert(`You can select a maximum of ${MAX_INITIAL_SKILL_PROFICIENCIES} skill proficiencies.`);
          newProficiencies = currentProficiencies;
        }
      }
      return { ...prevData, chosen_skill_proficiencies: newProficiencies };
    });
  };

  const parseIdList = (ids: (string | number)[]): number[] | null => {
    const num_ids = ids.map(id => typeof id === 'string' ? parseInt(id.trim(), 10) : id).filter(id => typeof id === 'number' && !isNaN(id) && id > 0);
    return num_ids.length > 0 ? num_ids : null;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!auth?.token) { setError("You must be logged in to create a character."); return; }
    setIsLoading(true); setError(null);

    const cantripIds = parseIdList(formData.chosen_cantrip_ids);
    const initialSpellIds = parseIdList(formData.chosen_initial_spell_ids);

    if (initialCantripsCount > 0 && (cantripIds?.length || 0) !== initialCantripsCount) {
        setError(`Please select exactly ${initialCantripsCount} unique cantrips for a ${formData.character_class}.`);
        setIsLoading(false); return;
    }
    if (initialSpellsCount > 0 && (initialSpellIds?.length || 0) !== initialSpellsCount) {
        setError(`Please select exactly ${initialSpellsCount} unique level 1 spells for a ${formData.character_class}.`);
        setIsLoading(false); return;
    }
    const allChosenSpellLikeIds = [...(cantripIds || []), ...(initialSpellIds || [])];
    if (new Set(allChosenSpellLikeIds).size !== allChosenSpellLikeIds.length) {
        setError("Spell/Cantrip choices must be unique.");
        setIsLoading(false); return;
    }
    
    const payload: CharacterCreatePayload = {
        name: formData.name,
        race: formData.race,
        character_class: formData.character_class,
        alignment: formData.alignment,
        background_story: formData.background_story,
        appearance_description: formData.appearance_description,
        strength: parseInt(formData.strength, 10),
        dexterity: parseInt(formData.dexterity, 10),
        constitution: parseInt(formData.constitution, 10),
        intelligence: parseInt(formData.intelligence, 10),
        wisdom: parseInt(formData.wisdom, 10),
        charisma: parseInt(formData.charisma, 10),
        chosen_cantrip_ids: cantripIds,
        chosen_initial_spell_ids: initialSpellIds,
        chosen_skill_proficiencies: formData.chosen_skill_proficiencies,
    };

    try {
      const newCharacter = await characterService.createCharacter(auth.token, payload);
      alert(`Character "${newCharacter.name}" created successfully!`);
      navigate(`/dashboard`); 
    } catch (err: any) {
      setError(err.message || "Failed to create character.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const pageStyle: React.CSSProperties = { padding: '20px', maxWidth: '800px', margin: '20px auto',};
  const formContainerStyle: React.CSSProperties = { backgroundColor: 'var(--parchment-highlight)', padding: '30px 40px', borderRadius: '8px', boxShadow: '0px 6px 18px rgba(0,0,0,0.15), 0px 0px 0px 1px var(--ink-color-light)', border: '1px solid rgba(120, 90, 70, 0.3)',};
  const titleStyle: React.CSSProperties = { fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)', fontSize: '2.8em', marginBottom: '1em', textAlign: 'center',};
  const errorStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', color: '#a02c2c', marginTop: '1em', minHeight: '1.2em', textAlign: 'center',};
  const abilityScoreGridStyle: React.CSSProperties = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5em', marginBottom: '1.5em'};
  const formGroupStyle: React.CSSProperties = { marginBottom: '1.2em', display: 'flex', flexDirection: 'column',};
  const labelStyle: React.CSSProperties = { display: 'block', fontFamily: 'var(--font-script-annotation)', fontSize: '1.1em', color: 'var(--ink-color-medium)', marginBottom: '0.4em', textAlign: 'left',};
  const selectStyle: React.CSSProperties = { fontFamily: 'var(--font-body-primary)', fontSize: '1.2em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', cursor: 'pointer',};
  const textAreaStyle: React.CSSProperties = { fontFamily: 'var(--font-handwritten-input)', fontSize: '1.5em', color: 'var(--ink-color-dark)', backgroundColor: 'rgba(245, 235, 215, 0.4)', border: '1px solid rgba(220, 210, 190, 0.7)', padding: '0.6em 0.9em', borderRadius: '3px', boxShadow: 'inset 1px 1px 4px rgba(0,0,0,0.08)', width: '100%', boxSizing: 'border-box', minHeight: '100px',};
  const skillCheckboxLabelStyle: React.CSSProperties = { marginLeft: '8px', cursor: 'pointer', fontFamily: 'var(--font-body-primary)'};
  const skillListItemStyle: React.CSSProperties = { display: 'flex', alignItems: 'center', marginBottom: '5px'};
  const skillListContainerStyle: React.CSSProperties = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '5px 15px', maxHeight: '250px', overflowY: 'auto', padding: '15px', border: '1px solid var(--ink-color-light)', borderRadius: '4px', backgroundColor: 'rgba(0,0,0,0.02)',};

  if (isLoading && allDndClasses.length === 0) return <div style={pageStyle}><p>Loading game data...</p></div>;

  return (
    <div style={pageStyle}>
      <div style={formContainerStyle}>
        <h1 style={titleStyle}>Chronicle a New Adventurer</h1>
        <form onSubmit={handleSubmit}>
          {/* ... Your form fields for name, race, class, alignment, etc. ... */}
          <div style={{display: 'flex', gap: '1.5em', flexWrap: 'wrap', marginTop: '1.2em' }}>
             <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}><label htmlFor="name" style={labelStyle}>Character Name:</label><ThemedInput id="name" name="name" type="text" value={formData.name} onChange={handleChange} placeholder="e.g., Eldrin Moonwhisper" disabled={isLoading} required /></div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}>
                <label htmlFor="race" style={labelStyle}>Race:</label>
                <select id="race" name="race" value={formData.race} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                    <option value="">-- Select Race --</option>{RACES.map(race => <option key={race} value={race}>{race}</option>)}
                </select>
            </div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}>
                <label htmlFor="character_class" style={labelStyle}>Class:</label>
                <select id="character_class" name="character_class" value={formData.character_class} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                    <option value="">-- Select Class --</option>{CLASSES.map(cls => <option key={cls} value={cls}>{cls}</option>)}
                </select>
            </div>
            <div style={{flex: 1, minWidth: '200px', ...formGroupStyle}}>
                <label htmlFor="alignment" style={labelStyle}>Alignment:</label>
                <select id="alignment" name="alignment" value={formData.alignment} onChange={handleChange} disabled={isLoading} style={selectStyle} required>
                    <option value="">-- Select Alignment --</option>{ALIGNMENTS.map(align => <option key={align} value={align}>{align}</option>)}
                </select>
            </div>
          </div>
          <h2 style={{fontFamily: 'var(--font-script-annotation)', fontSize: '1.5em', color: 'var(--ink-color-medium)', marginTop: '1.5em', marginBottom: '0.8em'}}>Ability Scores</h2>
          <div style={abilityScoreGridStyle}>
            {(['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const).map((stat) => (
              <ThemedInput key={stat} label={`${stat.charAt(0).toUpperCase() + stat.slice(1)}:`} id={stat} name={stat} type="number" value={formData[stat]} onChange={handleChange} min="1" max="20" disabled={isLoading} />
            ))}
          </div>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Skill Proficiencies (Choose up to {MAX_INITIAL_SKILL_PROFICIENCIES}):</label>
            {allAvailableSkills.length > 0 && (
              <div style={skillListContainerStyle}>
                {allAvailableSkills.map(skill => (
                  <div key={skill.id} style={skillListItemStyle}>
                    <input type="checkbox" id={`skill-prof-${skill.id}`} checked={formData.chosen_skill_proficiencies.includes(skill.id)} onChange={() => handleSkillProficiencyToggle(skill.id)} disabled={isLoading || (formData.chosen_skill_proficiencies.length >= MAX_INITIAL_SKILL_PROFICIENCIES && !formData.chosen_skill_proficiencies.includes(skill.id))}/>
                    <label htmlFor={`skill-prof-${skill.id}`} style={skillCheckboxLabelStyle}>{skill.name} ({skill.ability_modifier_name})</label>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div style={formGroupStyle}><label htmlFor="background_story" style={labelStyle}>Background Story:</label><textarea id="background_story" name="background_story" value={formData.background_story} onChange={handleChange} style={textAreaStyle} rows={4}/></div>
          <div style={formGroupStyle}><label htmlFor="appearance_description" style={labelStyle}>Appearance Description:</label><textarea id="appearance_description" name="appearance_description" value={formData.appearance_description} style={textAreaStyle} rows={3}/></div>
          
          {spellcastingInfo && (initialCantripsCount > 0 || initialSpellsCount > 0) && (
            <div style={{marginTop: '1.5em'}}>
              <h3 style={{fontFamily: 'var(--font-script-annotation)', fontSize: '1.3em', color: 'var(--ink-color-medium)', marginBottom: '0.8em'}}>Initial Spells (Lvl 1 {formData.character_class})</h3>
              {initialCantripsCount > 0 && (
                <div style={{marginBottom: '1em'}}>
                  <p style={labelStyle}>Choose {initialCantripsCount} Cantrips:</p>
                  {Array.from({ length: initialCantripsCount }).map((_, index) => (
                    <div key={`cantrip-select-${index}`} style={formGroupStyle}>
                      <select name={`chosen_cantrip_ids_${index}`} value={formData.chosen_cantrip_ids[index] || ""} onChange={(e) => handleSpellSelectionChange(e, index, 'cantrip')} style={selectStyle} required>
                        <option value="">-- Select Cantrip {index + 1} --</option>
                        {availableCantrips.map(spell => (<option key={spell.id} value={spell.id}>{spell.name}</option>))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
              {initialSpellsCount > 0 && (
                <div>
                  <p style={labelStyle}>Choose {initialSpellsCount} Level 1 Spells:</p>
                  {Array.from({ length: initialSpellsCount }).map((_, index) => (
                    <div key={`spell-select-${index}`} style={formGroupStyle}>
                      <select name={`chosen_initial_spell_ids_${index}`} value={formData.chosen_initial_spell_ids[index] || ""} onChange={(e) => handleSpellSelectionChange(e, index, 'spell')} style={selectStyle} required>
                        <option value="">-- Select Level 1 Spell {index + 1} --</option>
                        {availableL1Spells.map(spell => (<option key={spell.id} value={spell.id}>{spell.name}</option>))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {error && <p style={errorStyle}>{error}</p>}
          <div style={{ marginTop: '2.5em', textAlign: 'center' }}>
            <ThemedButton type="submit" disabled={isLoading}>{isLoading ? "Saving..." : "Begin Their Chronicle"}</ThemedButton>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCharacterPage;

