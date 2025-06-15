// Path: src/services/gameDataService.ts
import type { DndClass } from '../types/dndClass';
import type { Race } from '../types/race';
import type { Monster } from '../types/monster';
import type { SpellDefinition } from '../types/spell';
import type { ItemDefinition } from '../types/item';
import type { Background } from '../types/background';
import type { Condition } from '../types/condition';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const gameDataService = {
  /**
   * Fetches a list of all available D&D classes.
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
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch D&D classes (status: ${response.status})`);
    }
    return response.json() as Promise<DndClass[]>;
  },

  /**
   * Fetches a list of all available D&D races.
   */
  getRaces: async (token: string): Promise<Race[]> => {
    const response = await fetch(`${API_BASE_URL}/races/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch D&D races (status: ${response.status})`);
    }
    return response.json() as Promise<Race[]>;
  },

  /**
   * Fetches a list of all available monsters.
   */
  getMonsters: async (token: string): Promise<Monster[]> => {
    const response = await fetch(`${API_BASE_URL}/monsters/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch monsters (status: ${response.status})`);
    }
    return response.json() as Promise<Monster[]>;
  },

  /**
   * Fetches a list of all available spells.
   */
  getSpells: async (token: string): Promise<SpellDefinition[]> => {
    const response = await fetch(`${API_BASE_URL}/spells/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch spells (status: ${response.status})`);
    }
    return response.json() as Promise<SpellDefinition[]>;
  },

  /**
   * Fetches a list of all available items.
   */
  getItems: async (token: string): Promise<ItemDefinition[]> => {
    const response = await fetch(`${API_BASE_URL}/items/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch items (status: ${response.status})`);
    }
    return response.json() as Promise<ItemDefinition[]>;
  },

  getBackgrounds: async (token: string): Promise<Background[]> => {
    const response = await fetch(`${API_BASE_URL}/backgrounds/`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch D&D backgrounds (status: ${response.status})`);
    }
    return response.json() as Promise<Background[]>;
  },
  getConditions: async (token: string): Promise<Condition[]> => {
    const response = await fetch(`${API_BASE_URL}/conditions/`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
    });
    if (!response.ok) {
      if (response.status === 401) { throw new Error('Unauthorized: Session may have expired.'); }
      throw new Error(`Failed to fetch conditions (status: ${response.status})`);
    }
    return response.json() as Promise<Condition[]>;
  },
};

  
