// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Authentication Service for React Native
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = '@citylens:access_token';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string; // MongoDB ObjectId as string
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  is_active: boolean;
  role?: string;
  level?: number;
  points?: number;
  reputation_score?: number;
  is_verified?: boolean;
  is_admin?: boolean;
  created_at?: string;
  last_login?: string;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // OAuth2PasswordRequestForm requires application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Đăng nhập thất bại' }));
      throw new Error(error.detail || 'Đăng nhập thất bại');
    }

    const data: LoginResponse = await response.json();
    
    if (data.access_token) {
      await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
    }
    
    return data;
  }

  async register(userData: RegisterData): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Đăng ký thất bại' }));
      throw new Error(error.detail || 'Đăng ký thất bại');
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    const token = await this.getToken();
    if (!token) {
      throw new Error('Chưa đăng nhập');
    }

    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Không thể lấy thông tin người dùng');
    }

    return response.json();
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem(TOKEN_KEY);
  }

  async getToken(): Promise<string | null> {
    return AsyncStorage.getItem(TOKEN_KEY);
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await this.getToken();
    return !!token;
  }
}

export const authService = new AuthService();


