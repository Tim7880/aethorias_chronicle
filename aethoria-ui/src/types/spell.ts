// Path: src/types/spell.ts

// Using a string literal union type for type safety
export type FrontendSchoolOfMagic = 
    | "Abjuration"
    | "Conjuration"
    | "Divination"
    | "Enchantment"
    | "Evocation"
    | "Illusion"
    | "Necromancy"
    | "Transmutation"
    | "Universal";

// Optional: If you need an object to iterate over values
export const FrontendSchoolOfMagicEnumObject = {
    ABJURATION: "Abjuration",
    CONJURATION: "Conjuration",
    DIVINATION: "Divination",
    ENCHANTMENT: "Enchantment",
    EVOCATION: "Evocation",
    ILLUSION: "Illusion",
    NECROMANCY: "Necromancy",
    TRANSMUTATION: "Transmutation",
    UNIVERSAL: "Universal"
} as const;

export interface SpellDefinition {
  id: number;
  name: string;
  description: string;
  higher_level?: string | null;
  range: string;
  components: string;
  material?: string | null;
  ritual: boolean;
  duration: string;
  concentration: boolean;
  casting_time: string;
  level: number; 
  school: FrontendSchoolOfMagic; // Use the string literal union type
  dnd_classes?: string[] | null; 
  source_book?: string | null;
}

export interface CharacterSpell {
  id: number; 
  spell_id: number;
  is_known: boolean;
  is_prepared: boolean;
  spell_definition: SpellDefinition; 
}