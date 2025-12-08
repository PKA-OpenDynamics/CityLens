// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, User } from '../services/auth';

// ============================================
// TEMPORARY: Bypass login for testing
// Set to false to re-enable authentication
// ============================================
const BYPASS_LOGIN = true;

// ============================================
// Force show login screen even when bypass is enabled
// Set to true to view/login screen for UI editing
// ============================================
const FORCE_SHOW_LOGIN = false;

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock user data for testing when login is bypassed
const MOCK_USER: User = {
  id: 'mock-user-id',
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Người dùng Test',
  phone: '0123456789',
  is_active: true,
  role: 'user',
  level: 1,
  points: 0,
  reputation_score: 0,
  is_verified: false,
  is_admin: false,
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (FORCE_SHOW_LOGIN) {
      // Force show login screen for UI editing
      console.log('⚠️ FORCE SHOW LOGIN: Showing login screen for UI editing');
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    } else if (BYPASS_LOGIN) {
      // Bypass authentication - set mock user and mark as authenticated
      console.log('⚠️ LOGIN BYPASSED: Using mock user for testing');
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      setIsLoading(false);
    } else {
      // Normal authentication flow
      checkAuthStatus();
    }
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
    if (FORCE_SHOW_LOGIN) {
      // When forcing login screen, still allow login but use mock user if bypass is enabled
      if (BYPASS_LOGIN) {
        console.log('⚠️ FORCE SHOW LOGIN: Login called, using mock user');
        setUser(MOCK_USER);
        setIsAuthenticated(true);
        return;
      }
      // If not bypassing, use real login
      await authService.login({ username, password });
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      return;
    }
    if (BYPASS_LOGIN) {
      // When bypassing login, just set mock user
      console.log('⚠️ LOGIN BYPASSED: Login called but bypassed');
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      return;
    }
    await authService.login({ username, password });
    const userData = await authService.getCurrentUser();
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    if (BYPASS_LOGIN) {
      // When bypassing login, just clear mock user but keep authenticated for testing
      console.log('⚠️ LOGIN BYPASSED: Logout called but bypassed - staying authenticated');
      // Keep authenticated for testing purposes
      // setUser(null);
      // setIsAuthenticated(false);
      return;
    }
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshUser = async () => {
    if (BYPASS_LOGIN) {
      // When bypassing login, just refresh mock user
      setUser(MOCK_USER);
      return;
    }
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

