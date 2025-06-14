// Path: src/services/gameDataService.ts
import type { DndClass } from '../types/dndClass'; // We will create this type in the next step

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const gameDataService = {
  /**
   * Fetches a list of all available D&D classes.
   * @param token The user's authentication token.
   * @returns A promise that resolves to an array of DndClass objects.
   */
  getClasses: async (token: string): Promise<DndClass[]> => {
    const response = await fetch(`${API_BASE_URL}/classes/`, {
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
      throw new Error(`Failed to fetch D&D classes (status: ${response.status})`);
    }
    return response.json() as Promise<DndClass[]>;
  },

  // We can add getRaces, getMonsters, etc. here in the future.
};
