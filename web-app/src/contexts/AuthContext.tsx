// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, User } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    // Set a timeout to ensure loading doesn't last forever
    const timeoutId = setTimeout(() => {
      console.warn('Auth check taking too long, assuming not authenticated');
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }, 5000);

    try {
      const authenticated = await authService.isAuthenticated();
      if (authenticated) {
        try {
          const userData = await authService.getCurrentUser();
          clearTimeout(timeoutId);
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          // If getCurrentUser fails, user is not authenticated
          console.warn('Failed to get current user, clearing auth:', error);
          clearTimeout(timeoutId);
          await authService.logout();
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        clearTimeout(timeoutId);
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      clearTimeout(timeoutId);
      // On any error, assume not authenticated
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      // Always set loading to false, even on timeout or error
      clearTimeout(timeoutId);
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    await authService.login({ username, password });
    const userData = await authService.getCurrentUser();
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshUser = async () => {
    try {
      if (await authService.isAuthenticated()) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

