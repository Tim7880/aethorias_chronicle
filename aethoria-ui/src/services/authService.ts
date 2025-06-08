// Path: src/services/authService.ts
import type { User } from '../types/user';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface LoginCredentials {
  username: string; 
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

// --- NEW INTERFACE for the register payload ---
// This should match the UserCreate schema on the backend
export interface RegisterPayload {
    username: string;
    email: string;
    password: string;
    preferred_timezone?: string; // Optional
}
// --- END NEW INTERFACE ---


export const authService = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/login/token`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let errorDetail = `Login failed with status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          errorDetail = errorData.detail;
        }
      } catch (e) {
        // Could not parse JSON error
      }
      throw new Error(errorDetail);
    }
    return response.json() as Promise<TokenResponse>;
  },
  
  getCurrentUser: async (token: string): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('authToken'); 
      }
      throw new Error(`Failed to fetch current user (status: ${response.status})`);
    }
    return response.json() as Promise<User>;
  },
  
  // --- NEW FUNCTION for User Registration ---
  register: async (payload: RegisterPayload): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        let errorDetail = `Registration failed: ${response.status}`;
        try {
            const errorData = await response.json();
            // Handle cases where the error detail is a string or an array of Pydantic validation errors
            if (errorData && errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorDetail = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join(', ');
                } else {
                    errorDetail = errorData.detail;
                }
            }
        } catch (e) { /* Ignore if response body is not JSON */ }
        throw new Error(errorDetail);
    }
    // Backend returns the newly created User object on success
    return response.json() as Promise<User>;
  },
  // --- END NEW FUNCTION ---
};