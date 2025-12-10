// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { AI_API_BASE_URL } from '../config/env';

/**
 * Helper để đảm bảo URL luôn dùng HTTPS (trừ localhost)
 */
const ensureHttpsUrl = (url: string): string => {
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return url;
  }
  return url.replace(/^http:\/\//i, 'https://');
};

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

export interface ChatHistoryItem {
  _id: string;
  userId: string;
  message: string;
  response: string;
  sources?: string[];
  metadata?: Record<string, any>;
  timestamp?: string;
  createdAt?: string;
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
    // Sử dụng AI_API_BASE_URL từ env.ts và đảm bảo HTTPS
    this.baseUrl = ensureHttpsUrl(AI_API_BASE_URL);
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
   * Lấy lịch sử chat đã lưu trên backend (MongoDB Atlas)
   */
  async getHistory(
    {
      limit = 20,
      skip = 0,
      userId,
    }: { limit?: number; skip?: number; userId?: string },
    token?: string
  ): Promise<ApiResponse<ChatHistoryItem[]>> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const params = new URLSearchParams();
      params.set('limit', String(limit));
      params.set('skip', String(skip));
      if (userId) params.set('user_id', userId);

      const url = `${this.baseUrl}/history?${params.toString()}`;
      console.log('AI Chat History API:', url);

      const response = await fetch(url, { method: 'GET', headers });
      console.log('AI Chat History status:', response.status, response.statusText);

      const result = await response.json();
      if (!response.ok || result.success === false) {
        throw new Error(result.detail || result.error || 'Failed to fetch history');
      }

      return { success: true, data: result.data || [] };
    } catch (error: any) {
      console.error('Error fetching AI chat history:', error);
      return { success: false, error: error.message || 'Failed to fetch history' };
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

