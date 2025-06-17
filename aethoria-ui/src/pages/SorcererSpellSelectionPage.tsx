// Path: src/pages/SorcererSpellSelectionPage.tsx
import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { characterService } from '../services/characterService';
import { gameDataService } from '../services/gameDataService';
import type { Character, SorcererSpellSelectionRequest } from '../types/character';
import type { SpellDefinition } from '../types/spell';
import styles from './SorcererSpellSelectionPage.module.css';
import ThemedButton from '../components/common/ThemedButton';

const SorcererSpellSelectionPage: React.FC = () => {
    const { characterId } = useParams<{ characterId: string }>();
    const auth = useAuth();
    const navigate = useNavigate();

    const [character, setCharacter] = useState<Character | null>(null);
    const [allSpells, setAllSpells] = useState<SpellDefinition[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [newCantrips, setNewCantrips] = useState<number[]>([]);
    const [newSpells, setNewSpells] = useState<number[]>([]);
    
    // --- MODIFICATION: Removing unused state since spell swapping UI isn't built yet ---
    // const [spellToReplace, setSpellToReplace] = useState<number | null>(null);
    // const [replacementSpell, setReplacementSpell] = useState<number | null>(null);

    const SORCERER_SPELLS_KNOWN: { [key: number]: [number, number] } = {
        1: [4, 2], 2: [4, 3], 3: [4, 4], 4: [5, 5], 5: [5, 6], 6: [5, 7],
        7: [5, 8], 8: [5, 9], 9: [5, 10], 10: [6, 11], 11: [6, 12], 12: [6, 12],
        13: [6, 13], 14: [6, 13], 15: [6, 14], 16: [6, 14], 17: [6, 15], 18: [6, 15],
        19: [6, 15], 20: [6, 15],
    };

    const { numNewCantrips, numNewSpells, maxLearnableLevel } = useMemo(() => {
        if (!character) return { numNewCantrips: 0, numNewSpells: 0, maxLearnableLevel: 0 };
        const [targetCantrips, targetSpells] = SORCERER_SPELLS_KNOWN[character.level] || [0, 0];
        const knownCantrips = character.known_spells.filter(s => s.spell_definition.level === 0).length;
        const knownSpells = character.known_spells.filter(s => s.spell_definition.level > 0).length;
        
        let spellLevel = 0;
        if (character.level >= 17) spellLevel = 9;
        else if (character.level >= 15) spellLevel = 8;
        else if (character.level >= 13) spellLevel = 7;
        else if (character.level >= 11) spellLevel = 6;
        else if (character.level >= 9) spellLevel = 5;
        else if (character.level >= 7) spellLevel = 4;
        else if (character.level >= 5) spellLevel = 3;
        else if (character.level >= 3) spellLevel = 2;
        else if (character.level >= 1) spellLevel = 1;

        return {
            numNewCantrips: targetCantrips - knownCantrips,
            numNewSpells: targetSpells - knownSpells,
            maxLearnableLevel: spellLevel
        };
    }, [character]);

    useEffect(() => {
        const loadData = async () => {
            if (auth.token && characterId) {
                try {
                    const [charData, spellData] = await Promise.all([
                        characterService.getCharacterById(auth.token, parseInt(characterId, 10)),
                        gameDataService.getSpells(auth.token)
                    ]);
                    setCharacter(charData);
                    setAllSpells(spellData);
                } catch (err: any) {
                    setError(err.message || "Failed to load necessary data.");
                } finally {
                    setIsLoading(false);
                }
            }
        };
        loadData();
    }, [auth.token, characterId]);

    const handleCantripSelect = (spellId: number) => {
        setNewCantrips(prev => {
            if (prev.includes(spellId)) return prev.filter(id => id !== spellId);
            if (prev.length < numNewCantrips) return [...prev, spellId];
            return prev;
        });
    };

    const handleSpellSelect = (spellId: number) => {
        setNewSpells(prev => {
            if (prev.includes(spellId)) return prev.filter(id => id !== spellId);
            if (prev.length < numNewSpells) return [...prev, spellId];
            return prev;
        });
    };

    const handleSubmit = async () => {
        if (!auth.token || !characterId) return;

        if (newCantrips.length !== numNewCantrips) {
            setError(`Please select exactly ${numNewCantrips} new cantrip(s).`);
            return;
        }
        if (newSpells.length !== numNewSpells) {
            setError(`Please select exactly ${numNewSpells} new spell(s).`);
            return;
        }

        setError(null);
        setIsLoading(true);

        const payload: SorcererSpellSelectionRequest = {
            chosen_cantrip_ids_on_level_up: newCantrips,
            new_leveled_spell_ids: newSpells,
            // --- MODIFICATION: Set these to null as they are not used yet ---
            spell_to_replace_id: null,
            replacement_spell_id: null,
        };

        try {
            await characterService.selectSorcererSpells(auth.token, parseInt(characterId, 10), payload);
            alert("Spells updated successfully! Level up complete.");
            navigate(`/characters/${characterId}/view`);
        } catch (err: any) {
            setError(err.message || "Failed to save spell selections.");
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <div className={styles.pageContainer}><p>Loading...</p></div>;
    if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;
    if (!character) return <div className={styles.pageContainer}><p>Character not found.</p></div>;

    const knownSpellIds = new Set(character.known_spells.map(s => s.spell_id));
    // --- MODIFICATION: Added safety checks for dnd_classes ---
    const availableCantrips = allSpells.filter(s => s.level === 0 && s.dnd_classes?.includes("Sorcerer") && !knownSpellIds.has(s.id));
    const availableSpells = allSpells.filter(s => s.level > 0 && s.level <= maxLearnableLevel && s.dnd_classes?.includes("Sorcerer") && !knownSpellIds.has(s.id));

    return (
        <div className={styles.pageContainer}>
            <header className={styles.header}>
                <h1 className={styles.title}>Level Up: {character.name}</h1>
                <p className={styles.instructions}>Your Sorcerous power grows! Please make your spell selections.</p>
            </header>
            <div className={styles.selectionGrid}>
                {numNewCantrips > 0 && (
                    <div className={styles.column}>
                        <h2 className={styles.columnTitle}>Choose {numNewCantrips} New Cantrip(s)</h2>
                        <ul className={styles.spellList}>
                            {availableCantrips.map(spell => (
                                <li key={spell.id} onClick={() => handleCantripSelect(spell.id)} className={`${styles.spellItem} ${newCantrips.includes(spell.id) ? styles.selected : ''}`}>
                                    {spell.name}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                {numNewSpells > 0 && (
                    <div className={styles.column}>
                        <h2 className={styles.columnTitle}>Choose {numNewSpells} New Spell(s)</h2>
                        <ul className={styles.spellList}>
                            {availableSpells.map(spell => (
                                <li key={spell.id} onClick={() => handleSpellSelect(spell.id)} className={`${styles.spellItem} ${newSpells.includes(spell.id) ? styles.selected : ''}`}>
                                    {spell.name} (Lvl {spell.level})
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
            <div className={styles.buttonContainer}>
                <ThemedButton onClick={handleSubmit} disabled={isLoading}>
                    {isLoading ? "Saving..." : "Confirm Selections"}
                </ThemedButton>
            </div>
            {error && <p className={styles.errorText}>{error}</p>}
        </div>
    );
};

export default SorcererSpellSelectionPage;
