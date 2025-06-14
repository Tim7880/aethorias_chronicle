export interface RacialTrait {
    name: string;
    desc: string;
}

export interface Race {
    id: number;
    name: string;
    description: string | null;
    ability_score_increase: { [key: string]: number };
    size: string;
    speed: number;
    racial_traits: RacialTrait[] | null;
    languages: string | null;
}
