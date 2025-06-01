// Path: src/services/spellService.ts
import type { SpellDefinition } from '../types/spell'; // Assuming SpellDefinition is in src/types/spell.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface GetSpellsParams {
  level?: number;
  name?: string; // For searching by name later
  school?: string; // For filtering by school later
  // We might add a 'className' filter on the backend later for efficiency
}

export const spellService = {
  getSpells: async (token: string, params?: GetSpellsParams): Promise<SpellDefinition[]> => {
    const url = new URL(`${API_BASE_URL}/spells/`);
    if (params) {
      if (params.level !== undefined) url.searchParams.append('level', String(params.level));
      if (params.name) url.searchParams.append('name', params.name);
      if (params.school) url.searchParams.append('school', params.school);
    }
    // Note: The backend /spells/ endpoint currently doesn't use these filters yet,
    // but we can add them to the service now for future use.
    // For now, it will fetch all spells, and we'll filter on the frontend.

    const response = await fetch(url.toString(), {
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
      throw new Error(`Failed to fetch spells (status: ${response.status})`);
    }
    return response.json() as Promise<SpellDefinition[]>;
  },

  getSpellById: async (token: string, spellId: number): Promise<SpellDefinition> => {
    const response = await fetch(`<span class="math-inline">\{API\_BASE\_URL\}/spells/</span>{spellId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 401) throw new Error('Unauthorized');
        if (response.status === 404) throw new Error('Spell not found');
        throw new Error(`Failed to fetch spell ${spellId}`);
    }
    return response.json() as Promise<SpellDefinition>;
}
};