// Path: src/services/authService.ts
import type { User } from '../types/user';
// We'll use the backend API URL. For development, it's usually http://localhost:8000
// It's good practice to put this in an environment variable later.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface LoginCredentials {
  username: string; // Our backend login endpoint expects 'username' and 'password' in form data
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    // The backend /login/token endpoint expects 'application/x-www-form-urlencoded'
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/login/token`, {
      method: 'POST',
      headers: {
        // 'Content-Type': 'application/x-www-form-urlencoded', // fetch sets this for URLSearchParams
      },
      body: formData,
    });

    if (!response.ok) {
      // Try to parse error detail if available
      let errorDetail = `Login failed with status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          errorDetail = errorData.detail;
        }
      } catch (e) {
        // Could not parse JSON error, stick with status code
      }
      throw new Error(errorDetail);
    }
    return response.json() as Promise<TokenResponse>;
  },
  
  // --- NEW FUNCTION ---
  getCurrentUser: async (token: string): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // If token is invalid/expired, backend returns 401
      // We might want to clear the token from localStorage here too, or let AuthContext handle it
      if (response.status === 401) {
        localStorage.removeItem('authToken'); // Proactively clear bad token
      }
      throw new Error(`Failed to fetch current user (status: ${response.status})`);
    }
    return response.json() as Promise<User>;
  },
  // --- END NEW FUNCTION ---
  // We can add register, logout, getCurrentUser functions here later
  // Example:
  // getCurrentUser: async (token: string): Promise<any> => {
  //   const response = await fetch(`${API_BASE_URL}/users/me`, {
  //     headers: { 'Authorization': `Bearer ${token}` }
  //   });
  //   if (!response.ok) {
  //     throw new Error('Failed to fetch current user');
  //   }
  //   return response.json();
  // }
};