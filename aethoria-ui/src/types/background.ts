// Path: src/types/background.ts

export interface BackgroundFeature {
    name: string;
    desc: string;
}

export interface Background {
    id: number;
    name: string;
    description: string | null;
    skill_proficiencies: string[];
    tool_proficiencies: string | null;
    languages: string | null;
    equipment: string;
    feature: BackgroundFeature;
}
