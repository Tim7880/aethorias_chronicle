
// Path: src/types/monster.ts

export interface MonsterAbility {
    name: string;
    desc: string;
}

export interface MonsterAction extends MonsterAbility {
    // Actions can have more specific fields if needed in the future
    // e.g., attack_bonus, damage_dice, etc.
}

// This matches the `MonsterPublic` schema from the backend
export interface Monster {
    id: number;
    name: string;
    size: string;
    creature_type: string;
    alignment: string;
    armor_class: number;
    hit_dice: string;
    speed: { [key: string]: string };
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
    proficiencies: { value: number; proficiency: { name: string } }[] | null;
    damage_vulnerabilities: string[] | null;
    damage_resistances: string[] | null;
    damage_immunities: string[] | null;
    condition_immunities: string[] | null;
    senses: { [key: string]: string | number };
    languages: string;
    special_abilities: MonsterAbility[] | null;
    actions: MonsterAction[] | null;
    legendary_actions: MonsterAbility[] | null;
}
