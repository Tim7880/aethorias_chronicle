// Path: src/services/characterService.ts
import type { Character, CharacterHPLevelUpResponse, ASISelectionRequest } from '../types/character'; 
import type { ExpertiseSelectionRequest, RogueArchetypeSelectionRequest } from '../types/character'; // Assuming ExpertiseSelectionRequest is in schemas/character.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

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
  level?: number; 
  experience_points?: number;
  is_ascended_tier?: boolean;
  hit_points_max?: number | null;
  hit_points_current?: number | null;
  armor_class?: number | null;
  chosen_cantrip_ids?: number[] | null;
  chosen_initial_spell_ids?: number[] | null;
  chosen_skill_proficiencies?: number[] | null;
}

export const characterService = {
  getCharacters: async (token: string): Promise<Character[]> => {
    const response = await fetch(`${API_BASE_URL}/characters/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) throw new Error('Unauthorized: Session may have expired.');
      throw new Error(`Failed to fetch characters (status: ${response.status})`);
    }
    return response.json() as Promise<Character[]>;
  },

  createCharacter: async (token: string, characterData: CharacterCreatePayload): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(characterData),
    });
    if (!response.ok) {
      let errorDetail = `Character creation failed: ${response.status}`;
      try { const errorData = await response.json(); if (errorData && errorData.detail) { if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg || "Unknown error").join(', '); } else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail; }}} catch (e) {}
      throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  },

  confirmHPIncrease: async (
    token: string, characterId: number, method: 'average' | 'roll'
  ): Promise<CharacterHPLevelUpResponse> => {
    const response = await fetch(`${API_BASE_URL}/characters/${characterId}/level-up/confirm-hp`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ method }),
    });
    if (!response.ok) {
      let errorDetail = `Confirming HP increase failed: ${response.status}`;
      try { const errorData = await response.json(); if (errorData && errorData.detail) { if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg).join(', ');} else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail;}}} catch (e) {}
      throw new Error(errorDetail);
    }
    return response.json() as Promise<CharacterHPLevelUpResponse>;
  },

  getCharacterById: async (token: string, characterId: number): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/${characterId}`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
        let errorDetail = `Failed to fetch character ${characterId}: ${response.status}`;
        try { const errorData = await response.json(); if (errorData && errorData.detail) { if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg).join(', ');} else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail;}}} catch (e) {}
        if (response.status === 404) throw new Error("Character not found.");
        if (response.status === 401) throw new Error("Unauthorized.");
        throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  },

  // --- NEW FUNCTION for Rogue Expertise Selection ---
  selectRogueExpertise: async (
    token: string,
    characterId: number,
    payload: ExpertiseSelectionRequest // This type needs to be imported/defined
  ): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/${characterId}/level-up/select-expertise`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let errorDetail = `Selecting expertise failed: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg).join(', ');}
          else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail;}
        }
      } catch (e) {/*ignore json parse error if any*/}
      throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  },
  // --- END NEW FUNCTION ---

  selectRogueArchetype: async (
    token: string,
    characterId: number,
    payload: RogueArchetypeSelectionRequest 
  ): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/${characterId}/level-up/select-archetype`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let errorDetail = `Selecting archetype failed: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg).join(', ');}
          else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail;}
        }
      } catch (e) {/*ignore json parse error if any*/}
      throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  },

  // --- NEW FUNCTION for ASI Selection ---
  selectASI: async (
    token: string,
    characterId: number,
    payload: ASISelectionRequest 
  ): Promise<Character> => {
    const response = await fetch(`${API_BASE_URL}/characters/${characterId}/level-up/select-asi`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let errorDetail = `Selecting ASI failed: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          if (Array.isArray(errorData.detail)) { errorDetail = errorData.detail.map((err: any) => err.msg).join(', ');}
          else if (typeof errorData.detail === 'string') { errorDetail = errorData.detail;}
        }
      } catch (e) {/*ignore json parse error if any*/}
      throw new Error(errorDetail);
    }
    return response.json() as Promise<Character>;
  }
  // --- END NEW FUNCTION ---
};
