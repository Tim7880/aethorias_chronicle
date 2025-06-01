// Path: src/services/characterService.ts
import type { Character } from '../types/character'; // Import our frontend Character interface

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

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
      // Handle error, e.g., token expired, not authorized
      if (response.status === 401) {
        // Could trigger a logout or token refresh mechanism here
        throw new Error('Unauthorized: Session may have expired.');
      }
      throw new Error(`Failed to fetch characters (status: ${response.status})`);
    }
    return response.json() as Promise<Character[]>;
  },

  // We will add createCharacter, getCharacterById, updateCharacter, etc. here later
};