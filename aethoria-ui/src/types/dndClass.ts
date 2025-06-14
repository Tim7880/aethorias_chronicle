// Path: src/types/dndClass.ts

// This represents the data for a single level of a class
export interface ClassLevel {
    id: number;
    level: number;
    proficiency_bonus: number;
    features: { name: string; desc: string }[];
    spellcasting?: { [key: string]: number } | null;
}

// This represents the full D&D Class object
export interface DndClass {
    id: number;
    name: string;
    description: string | null;
    hit_die: number;
    levels: ClassLevel[];
}
