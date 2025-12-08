// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

interface AuthContextType {
  isAuthenticated: boolean;
  userEmail: string | null;
  login: (email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  userEmail: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication on mount
    const authStatus = localStorage.getItem("isAuthenticated");
    const email = localStorage.getItem("userEmail");

    if (authStatus === "true" && email) {
      setIsAuthenticated(true);
      setUserEmail(email);
    }

    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Redirect logic
    if (isLoading) return;

    const publicPaths = ["/login", "/signup"];
    const isPublicPath = publicPaths.includes(pathname);

    if (!isAuthenticated && !isPublicPath) {
      router.push("/login");
    }

    if (isAuthenticated && isPublicPath) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, pathname, router, isLoading]);

  const login = (email: string) => {
    localStorage.setItem("isAuthenticated", "true");
    localStorage.setItem("userEmail", email);
    setIsAuthenticated(true);
    setUserEmail(email);
  };

  const logout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userEmail");
    setIsAuthenticated(false);
    setUserEmail(null);
    router.push("/login");
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
    <AuthContext.Provider value={{ isAuthenticated, userEmail, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
