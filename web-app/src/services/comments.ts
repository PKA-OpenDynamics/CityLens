// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { REPORTS_API_BASE_URL } from '../config/env';



export interface Comment {
  _id: string;
  reportId: string;
  userId?: string | null;
  userName?: string | null;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  count?: number;
}

class CommentsService {
  private baseUrl: string;

  constructor() {
    // Sử dụng REPORTS_API_BASE_URL từ env.ts
    this.baseUrl = REPORTS_API_BASE_URL;
    console.log('[CommentsService] baseUrl:', this.baseUrl);
  }

  /**
   * Lấy danh sách comments của một report từ MongoDB Atlas
   */
  async getComments(
    reportId: string,
    options?: {
      limit?: number;
      skip?: number;
    }
  ): Promise<Comment[]> {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', options.limit.toString());
      if (options?.skip) params.append('skip', options.skip.toString());

      const queryString = params.toString();
      const url = `${this.baseUrl}/reports/${reportId}/comments${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to fetch comments');
      }

      if (result.success && result.data) {
        return result.data;
      }
      return [];
    } catch (error) {
      console.error('Error getting comments:', error);
      return [];
    }
  }

  /**
   * Thêm comment mới vào MongoDB Atlas
   */
  async addComment(
    reportId: string,
    content: string,
    userId?: string,
    userName?: string
  ): Promise<Comment> {
    try {
      const response = await fetch(`${this.baseUrl}/reports/${reportId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content.trim(),
          userId: userId || undefined,
          userName: userName || undefined,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to add comment');
      }

      if (result.success && result.data) {
        return result.data;
      }
      throw new Error('Invalid response from server');
    } catch (error: any) {
      console.error('Error adding comment:', error);
      throw error;
    }
  }

  /**
   * Xóa comment từ MongoDB Atlas
   */
  async deleteComment(commentId: string, userId?: string): Promise<boolean> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('userId', userId);

      const queryString = params.toString();
      const url = `${this.baseUrl}/reports/comments/${commentId}${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to delete comment');
      }

      return result.success === true;
    } catch (error: any) {
      console.error('Error deleting comment:', error);
      throw error;
    }
  }

  /**
   * Đếm số lượng comments của một report
   */
  async countComments(reportId: string): Promise<number> {
    try {
      const comments = await this.getComments(reportId);
      return comments.length;
    } catch (error) {
      console.error('Error counting comments:', error);
      return 0;
    }
  }
}

export default new CommentsService();

