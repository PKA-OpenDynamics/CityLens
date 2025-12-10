// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // Increased timeout for slow connections
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          // Use admin_token for admin endpoints, access_token for others
          const adminToken = localStorage.getItem('admin_token');
          const accessToken = localStorage.getItem('access_token');
          
          // Skip if header already set (for app reports with explicit token)
          if (!config.headers.Authorization) {
            if (adminToken) {
              config.headers.Authorization = `Bearer ${adminToken}`;
            } else if (accessToken) {
              config.headers.Authorization = `Bearer ${accessToken}`;
            }
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Only redirect to login for non-app endpoints and when it's a real auth error
        const url = error.config?.url || '';
        const isAppEndpoint = url.includes('/app/');
        
        if (error.response?.status === 401 && typeof window !== 'undefined' && !isAppEndpoint) {
          // Don't auto-redirect, just remove tokens
          // Let the auth context handle the redirect
          console.warn('Unauthorized request to:', url);
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: { headers?: Record<string, string> }): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: { headers?: Record<string, string> }): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: { params?: any }): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: { headers?: Record<string, string>; params?: any }): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();
