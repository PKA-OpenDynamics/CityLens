// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { apiClient } from './api-client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  department?: string;
  position?: string;
  reason?: string;
}

export interface UserProfile {
  _id: string;
  email: string;
  full_name: string;
  phone?: string;
  department?: string;
  position?: string;
  avatar_url?: string;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  user: UserProfile;
  token: Token;
  message: string;
}

export interface RegisterResponse {
  user: UserProfile;
  message: string;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    
    // Store tokens
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', response.token.access_token);
      localStorage.setItem('refresh_token', response.token.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('userEmail', response.user.email);
    }
    
    return response;
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>('/auth/register', data);
    return response;
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/auth/me');
    
    // Update stored user
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(response));
    }
    
    return response;
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>('/auth/me', data);
    
    // Update stored user
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(response));
    }
    
    return response;
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response;
  },

  async refreshToken(refreshToken: string): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/refresh', { refresh_token: refreshToken });
    
    // Update tokens
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    
    return response;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('userEmail');
    }
  },

  getStoredUser(): UserProfile | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch {
          return null;
        }
      }
    }
    return null;
  },

  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('isAuthenticated') === 'true' && !!localStorage.getItem('access_token');
    }
    return false;
  },
};
