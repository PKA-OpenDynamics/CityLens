// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * App Reports API Service
 * Connects to Mobile App Reports endpoints (MongoDB Atlas)
 */

import { apiClient } from './api-client';

// ============================================
// Types
// ============================================

export interface MediaItem {
  uri: string;
  type: 'image' | 'video';
  filename?: string;
}

export interface LocationData {
  lat: number;
  lng: number;
}

export interface AppReport {
  _id: string;
  reportType: string;
  ward: string;
  addressDetail: string;
  location?: LocationData;
  title: string;
  content: string;
  media: MediaItem[];
  userId?: string;
  status: 'pending' | 'processing' | 'resolved' | 'rejected';
  adminNote?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppReportListResponse {
  success: boolean;
  data: AppReport[];
  count: number;
}

export interface AppReportResponse {
  success: boolean;
  data: AppReport;
}

export interface AppReportStats {
  total: number;
  pending: number;
  processing: number;
  resolved: number;
  rejected: number;
}

export interface AppReportStatsResponse {
  success: boolean;
  data: AppReportStats;
}

export interface AppComment {
  _id: string;
  reportId: string;
  userId?: string;
  userName: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppCommentListResponse {
  success: boolean;
  data: AppComment[];
  count: number;
}

export interface AppCommentResponse {
  success: boolean;
  data: AppComment;
}

// Report type options - using Lucide icon names
export const REPORT_TYPES = [
  { value: 'infrastructure', label: 'Hạ tầng', icon: 'building-2' },
  { value: 'environment', label: 'Môi trường', icon: 'trees' },
  { value: 'security', label: 'An ninh trật tự', icon: 'shield' },
  { value: 'traffic', label: 'Giao thông', icon: 'car' },
  { value: 'sanitation', label: 'Vệ sinh', icon: 'trash-2' },
  { value: 'lighting', label: 'Chiếu sáng', icon: 'lightbulb' },
  { value: 'water', label: 'Cấp thoát nước', icon: 'droplets' },
  { value: 'other', label: 'Khác', icon: 'file-text' },
];

// Status options
export const REPORT_STATUSES = [
  { value: 'pending', label: 'Chờ xử lý', color: 'yellow' },
  { value: 'processing', label: 'Đang xử lý', color: 'blue' },
  { value: 'resolved', label: 'Đã xử lý', color: 'green' },
  { value: 'rejected', label: 'Từ chối', color: 'red' },
];

// ============================================
// API Functions
// ============================================

import { apiCache } from './api-cache';

export const appReportsApi = {
  /**
   * Get reports list with optional filters (optimized with caching)
   */
  getReports: async (params?: {
    status?: string;
    userId?: string;
    limit?: number;
    skip?: number;
    include_media?: boolean;  // Set to false for faster loading
    useCache?: boolean;  // Enable/disable caching (default: true)
  }): Promise<AppReportListResponse> => {
    try {
      const { useCache = true, ...apiParams } = params || {};
      
      // Check cache first (with 2 minute TTL)
      if (useCache) {
        const cached = apiCache.get<AppReportListResponse>('/app/reports/', apiParams);
        if (cached) {
          return cached;
        }
      }
      
      const response = await apiClient.get<AppReportListResponse>('/app/reports/', apiParams);
      
      // Cache successful response
      if (useCache && response.success) {
        apiCache.set('/app/reports/', response, apiParams, 2 * 60 * 1000); // 2 minutes
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching app reports:', error);
      return { success: false, data: [], count: 0 };
    }
  },

  /**
   * Get reports summary (optimized for map view - no media, with caching)
   * Much faster than full reports list
   */
  getReportsSummary: async (params?: {
    status?: string;
    limit?: number;
    skip?: number;
    useCache?: boolean;
  }): Promise<AppReportListResponse> => {
    try {
      const { useCache = true, ...apiParams } = params || {};
      
      // Check cache first (with 3 minute TTL for summary)
      if (useCache) {
        const cached = apiCache.get<AppReportListResponse>('/app/reports/summary/all', apiParams);
        if (cached) {
          return cached;
        }
      }
      
      const response = await apiClient.get<AppReportListResponse>('/app/reports/summary/all', apiParams);
      
      // Cache successful response
      if (useCache && response.success) {
        apiCache.set('/app/reports/summary/all', response, apiParams, 3 * 60 * 1000); // 3 minutes
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching reports summary:', error);
      return { success: false, data: [], count: 0 };
    }
  },

  /**
   * Get a single report by ID
   */
  getReport: async (reportId: string): Promise<AppReportResponse> => {
    return apiClient.get<AppReportResponse>(`/app/reports/${reportId}`);
  },

  /**
   * Update report status (Admin only)
   * Invalidates cache after successful update
   */
  updateStatus: async (
    reportId: string,
    status: string,
    adminNote?: string,
    token?: string
  ): Promise<AppReportResponse> => {
    try {
      // Get token from parameter or localStorage
      const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('admin_token') : null);
      
      const headers: Record<string, string> = {};
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      
      const response = await apiClient.put<AppReportResponse>(
        `/app/reports/${reportId}`,
        { status, adminNote },
        { headers }
      );
      
      // Invalidate all reports cache after successful update
      if (response.success) {
        apiCache.invalidatePattern(/^\/app\/reports/);
      }
      
      return response;
    } catch (error: any) {
      console.error('Error updating report status:', error);
      // Return error response instead of throwing to prevent logout
      return {
        success: false,
        data: {} as any,
      };
    }
  },

  /**
   * Delete a report (Admin only)
   */
  deleteReport: async (reportId: string, token?: string): Promise<{ success: boolean; message: string }> => {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return apiClient.delete(`/app/reports/${reportId}`, { headers });
  },

  /**
   * Get report statistics
   */
  getStats: async (userId?: string): Promise<AppReportStatsResponse> => {
    try {
      const params = userId ? { userId } : undefined;
      const response = await apiClient.get<AppReportStatsResponse>('/app/reports/stats/summary', params);
      return response;
    } catch (error) {
      console.error('Error fetching report stats:', error);
      return {
        success: false,
        data: { total: 0, pending: 0, processing: 0, resolved: 0, rejected: 0 }
      };
    }
  },

  /**
   * Get comments for a report
   */
  getComments: async (
    reportId: string,
    params?: { limit?: number; skip?: number }
  ): Promise<AppCommentListResponse> => {
    try {
      const response = await apiClient.get<AppCommentListResponse>(
        `/app/reports/${reportId}/comments`,
        params
      );
      return response;
    } catch (error) {
      console.error('Error fetching comments:', error);
      return { success: false, data: [], count: 0 };
    }
  },

  /**
   * Create a new comment
   */
  createComment: async (
    reportId: string,
    content: string,
    userId?: string,
    userName?: string
  ): Promise<AppCommentResponse> => {
    return apiClient.post<AppCommentResponse>(`/app/reports/${reportId}/comments`, {
      content,
      userId,
      userName,
    });
  },

  /**
   * Delete a comment
   */
  deleteComment: async (
    commentId: string,
    userId?: string
  ): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete(`/app/reports/comments/${commentId}`, {
      params: { userId },
    });
  },
};

// Helper functions
export const getReportTypeLabel = (type: string): string => {
  const found = REPORT_TYPES.find(t => t.value === type);
  return found ? found.label : type;
};

export const getReportTypeIcon = (type: string): string => {
  const found = REPORT_TYPES.find(t => t.value === type);
  return found ? found.icon : '📋';
};

export const getStatusLabel = (status: string): string => {
  const found = REPORT_STATUSES.find(s => s.value === status);
  return found ? found.label : status;
};

export const getStatusColor = (status: string): string => {
  const found = REPORT_STATUSES.find(s => s.value === status);
  return found ? found.color : 'gray';
};

export const formatTimeAgo = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    
    if (diffMs < 0) return 'Vừa xong';
    
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    if (diffDays < 7) return `${diffDays} ngày trước`;
    return date.toLocaleDateString('vi-VN');
  } catch {
    return dateString;
  }
};
