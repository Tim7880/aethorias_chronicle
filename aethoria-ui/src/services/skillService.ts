// Path: src/services/skillService.ts
import type { SkillDefinition } from '../types/skill'; // Assuming SkillDefinition is in src/types/skill.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const skillService = {
  /**
   * Fetches all available skills.
   * The backend /api/v1/skills/ endpoint should be accessible with authentication.
   */
  getSkills: async (token: string): Promise<SkillDefinition[]> => {
    const response = await fetch(`${API_BASE_URL}/skills/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized: Session may have expired. Could not fetch skills.');
      }
      throw new Error(`Failed to fetch skills (status: ${response.status})`);
    }
    return response.json() as Promise<SkillDefinition[]>;
  },

  // We can add other skill-related service functions here later if needed
  // e.g., getSkillById, etc.
};

