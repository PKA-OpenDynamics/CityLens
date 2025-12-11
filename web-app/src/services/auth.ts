// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Authentication Service for React Native
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { AUTH_API_BASE_URL } from '../config/env';

const API_BASE = AUTH_API_BASE_URL;
console.log('[AuthService] API_BASE:', API_BASE);
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
  _id?: string; // MongoDB ObjectId
  id?: string; // Alias for _id (for compatibility)
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
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: credentials.username,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Đăng nhập thất bại' }));
      throw new Error(error.error || error.detail || 'Đăng nhập thất bại');
    }

    const result = await response.json();
    
    if (result.success && result.data?.access_token) {
      await AsyncStorage.setItem(TOKEN_KEY, result.data.access_token);
      return {
        access_token: result.data.access_token,
        token_type: result.data.token_type || 'bearer',
      };
    }
    
    throw new Error('Đăng nhập thất bại');
  }

  async register(userData: RegisterData): Promise<User> {
    const requestBody = {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      full_name: userData.full_name,
      phone: userData.phone,
    };
    
    console.log('Register request:', { url: `${API_BASE}/auth/register`, body: { ...requestBody, password: '***' } });
    
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    const responseData = await response.json().catch(() => ({ error: 'Đăng ký thất bại' }));
    console.log('Register response:', { status: response.status, data: responseData });

    if (!response.ok) {
      throw new Error(responseData.error || responseData.detail || 'Đăng ký thất bại');
    }

    const result = await response.json();
    
    if (result.success && result.data?.user) {
      // Save token if provided
      if (result.data.access_token) {
        await AsyncStorage.setItem(TOKEN_KEY, result.data.access_token);
      }
      // Map _id to id for compatibility
      const user = result.data.user;
      if (user._id && !user.id) {
        user.id = user._id;
      }
      return user;
    }
    
    throw new Error('Đăng ký thất bại');
  }

  async getCurrentUser(): Promise<User> {
    const token = await this.getToken();
    if (!token) {
      throw new Error('Chưa đăng nhập');
    }

    const response = await fetch(`${API_BASE}/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Không thể lấy thông tin người dùng' }));
      throw new Error(error.error || 'Không thể lấy thông tin người dùng');
    }

    const result = await response.json();
    
    if (result.success && result.data) {
      // Map _id to id for compatibility
      const user = result.data;
      if (user._id && !user.id) {
        user.id = user._id;
      }
      return user;
    }
    
    throw new Error('Không thể lấy thông tin người dùng');
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


