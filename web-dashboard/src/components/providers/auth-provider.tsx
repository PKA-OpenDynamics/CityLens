// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authService, UserProfile } from "@/lib/auth-service";

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserProfile | null;
  login: () => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication on mount
    const checkAuth = async () => {
      const isAuth = authService.isAuthenticated();
      const storedUser = authService.getStoredUser();

      if (isAuth && storedUser) {
        setIsAuthenticated(true);
        setUser(storedUser);
        
        // Optionally refresh user profile from server
        try {
          const freshUser = await authService.getProfile();
          setUser(freshUser);
        } catch (error) {
          console.error('Failed to refresh user profile:', error);
          // Keep using stored user if refresh fails
        }
      }

      setIsLoading(false);
    };

    checkAuth();
  }, []);

  useEffect(() => {
    // Redirect logic
    if (isLoading) return;

    const publicPaths = ["/login", "/signup", "/"];
    const isPublicPath = publicPaths.includes(pathname);

    // If not authenticated and trying to access protected route
    if (!isAuthenticated && !isPublicPath) {
      router.push("/login");
      return;
    }

    // If authenticated and on login/signup page, redirect to dashboard
    if (isAuthenticated && (pathname === "/login" || pathname === "/signup")) {
      router.push("/dashboard");
      return;
    }

    // Home page is handled by its own useEffect
  }, [isAuthenticated, pathname, router, isLoading]);

  const login = () => {
    // This is called after successful API login
    const storedUser = authService.getStoredUser();
    if (storedUser) {
      setIsAuthenticated(true);
      setUser(storedUser);
    }
  };

  const logout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    router.push("/login");
  };

  const refreshUser = async () => {
    try {
      const freshUser = await authService.getProfile();
      setUser(freshUser);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // If refresh fails with 401, logout
      if ((error as any)?.response?.status === 401) {
        logout();
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
