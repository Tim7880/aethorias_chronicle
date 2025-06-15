// Path: src/types/race.ts

export interface RacialTrait {
    name: string;
    desc: string;
}

// --- NEW: Interface for a single subrace ---
export interface SubRace {
    name: string;
    description?: string | null;
    ability_score_increase: { [key: string]: number };
    racial_traits?: RacialTrait[] | null;
}
// --- END NEW ---

export interface Race {
    id: number;
    name: string;
    description: string | null;
    ability_score_increase: { [key: string]: number };
    size: string;
    speed: number;
    racial_traits: RacialTrait[] | null;
    languages: string | null;
    // --- ADDED: subraces property ---
    subraces?: SubRace[] | null;
}

