// Path: src/contexts/AuthContext.tsx
import React, { createContext, useState, useContext, useEffect } from 'react';
// useNavigate is no longer needed in this context file
import { authService } from '../services/authService';
import type { User } from '../types/user';
import type { ReactNode } from 'react';
interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const bootstrapAuth = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        setToken(storedToken);
        try {
          const currentUser = await authService.getCurrentUser(storedToken);
          setUser(currentUser);
          setIsAuthenticated(true);
        } catch (err) {
          console.error("Token validation failed:", err);
          localStorage.removeItem('authToken');
          setToken(null);
          setUser(null);
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };
    bootstrapAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenResponse = await authService.login(credentials);
      localStorage.setItem('authToken', tokenResponse.access_token);
      setToken(tokenResponse.access_token);
      
      const currentUser = await authService.getCurrentUser(tokenResponse.access_token);
      setUser(currentUser);
      setIsAuthenticated(true);
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Login failed.');
      setIsLoading(false);
      throw err;
    }
  };

  const logout = () => {
    // --- START MODIFICATION ---
    // Clear all authentication state first
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    
    // Then, force a full page navigation to the landing page.
    // This bypasses React Router's state-based redirection and is guaranteed to work.
    window.location.assign('/');
    // --- END MODIFICATION ---
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

