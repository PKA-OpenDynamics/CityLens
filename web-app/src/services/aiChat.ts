// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { AUTH_API_BASE_URL } from '../config/env';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  user_location?: {
    latitude: number;
    longitude: number;
  };
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  sources?: string[];
  timestamp: string;
  metadata?: {
    intent?: any;
    has_location?: boolean;
    error?: string;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

class AIChatService {
  private baseUrl: string;

  constructor() {
    const authBase = AUTH_API_BASE_URL || 'http://localhost:8000/api/v1/app';
    // Build AI chat base URL from auth API base URL
    if (authBase.includes('/auth')) {
      this.baseUrl = authBase.replace('/auth', '/ai');
    } else if (authBase.endsWith('/app')) {
      this.baseUrl = `${authBase}/ai`;
    } else {
      this.baseUrl = `${authBase}/ai`;
    }
    // Fallback to default
    if (!this.baseUrl || this.baseUrl === '/ai') {
      this.baseUrl = 'http://localhost:8000/api/v1/app/ai';
    }
  }

  /**
   * Chat với AI CityLens
   */
  async chat(request: ChatRequest, token?: string): Promise<ApiResponse<ChatResponse>> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const url = `${this.baseUrl}/chat`;
      console.log('Calling AI Chat API:', url, 'with body:', JSON.stringify(request));
      
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      console.log('AI Chat API Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('AI Chat API Error response:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { detail: errorText || `HTTP ${response.status}: ${response.statusText}` };
        }
        throw new Error(errorData.message || errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('AI Chat API Success response:', result);

      return {
        success: true,
        data: result,
      };
    } catch (error: any) {
      console.error('Error chatting with AI:', error);
      return {
        success: false,
        error: error.message || 'Failed to chat with AI',
      };
    }
  }

  /**
   * Kiểm tra trạng thái của AI chat service
   */
  async checkHealth(): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      return {
        success: response.ok,
        data: result,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Failed to check AI chat health',
      };
    }
  }
}

export const aiChatService = new AIChatService();

