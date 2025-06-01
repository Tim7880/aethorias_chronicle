// Path: src/services/characterService.ts
import type { Character } from '../types/character'; // Our frontend Character interface

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// This interface should match the fields expected by your backend's CharacterCreate schema
// We'll need to be careful about converting form strings to numbers for stats here.
export interface CharacterCreatePayload {
  name: string;
  race?: string | null;
  character_class?: string | null;
  alignment?: string | null;
  background_story?: string | null;
  appearance_description?: string | null;

  strength?: number | null;
  dexterity?: number | null;
  constitution?: number | null;
  intelligence?: number | null;
  wisdom?: number | null;
  charisma?: number | null;

  // These are typically defaulted by backend or set based on L1 choices/class
  level?: number; 
  experience_points?: number;
  is_ascended_tier?: boolean;
  hit_points_max?: number | null;
  hit_points_current?: number | null;
  armor_class?: number | null;

  // For L1 Sorcerer/caster initial spell selection (as defined in CharacterCreate schema)
  chosen_cantrip_ids?: number[] | null;
  chosen_initial_spell_ids?: number[] | null;
}


export const characterService = {
  getCharacters: async (token: string): Promise<Character[]> => {
    const response = await fetch(`${API_BASE_URL}/characters/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized: Session may have expired.');
      }
      throw new Error(`Failed to fetch characters (status: ${response.status})`);
    }
    return response.json() as Promise<Character[]>;
  },

  // --- NEW FUNCTION ---
  createCharacter: async (token: string, characterData: CharacterCreatePayload): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(characterData),
    });

    if (!response.ok) {
      // Try to parse error detail if available
      let errorDetail = `Character creation failed with status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          // FastAPI often returns errors in an array or a single detail object
          if (Array.isArray(errorData.detail)) {
            errorDetail = errorData.detail.map((err: any) => err.msg || "Unknown error").join(', ');
          } else if (typeof errorData.detail === 'string') {
            errorDetail = errorData.detail;
          }
        }
      } catch (e) { /* Could not parse JSON error */ }
      throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  }
  // --- END NEW FUNCTION ---
};

