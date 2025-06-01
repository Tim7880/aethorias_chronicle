// Path: src/contexts/AuthContext.tsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService } from '../services/authService'; // We'll add getCurrentUser here
import type { User } from '../types/user'; // Our frontend User interface

// Define the shape of the login credentials for the context's login function
interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean; // For loading state during auth operations
  error: string | null;   // For storing login/auth errors
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  // fetchCurrentUser: () => Promise<void>; // We can call this internally on load
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState<boolean>(true); // Start true to check token on load
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const bootstrapAuth = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        setToken(storedToken);
        try {
          // Validate token by fetching current user
          const currentUser = await authService.getCurrentUser(storedToken);
          setUser(currentUser);
          setIsAuthenticated(true);
          setError(null);
        } catch (err) {
          console.error("Failed to fetch current user with stored token", err);
          // Token might be invalid or expired
          localStorage.removeItem('authToken');
          setToken(null);
          setUser(null);
          setIsAuthenticated(false);
          setError("Session expired or token invalid. Please log in again.");
        }
      }
      setIsLoading(false);
    };
    bootstrapAuth();
  }, []); // Empty dependency array means this runs once on mount

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenResponse = await authService.login(credentials);
      localStorage.setItem('authToken', tokenResponse.access_token);
      setToken(tokenResponse.access_token);
      // After setting token, fetch user details
      const currentUser = await authService.getCurrentUser(tokenResponse.access_token);
      setUser(currentUser);
      setIsAuthenticated(true);
      setIsLoading(false);
    } catch (err: any) {
      console.error('Login failed in AuthContext:', err);
      setError(err.message || 'Login failed. Please check your credentials.');
      setIsLoading(false);
      throw err; // Re-throw to allow LoginPage to handle it if needed
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    // Optionally, navigate to login page or landing page here using window.location or if router is accessible
    // For now, just clears state. Navigation will be handled by components using this.
    console.log("User logged out");
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};