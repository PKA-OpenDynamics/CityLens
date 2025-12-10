// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { REPORTS_API_BASE_URL } from '../config/env';

export interface ReportMedia {
  uri: string;
  type: 'image' | 'video';
  filename?: string;
}

export interface CreateReportData {
  reportType: string;
  ward: string;
  addressDetail?: string;
  location?: {
    lat: number;
    lng: number;
  };
  title?: string;
  content: string;
  media: ReportMedia[];
  userId?: string;
}

export interface Report {
  _id: string;
  reportType: string;
  ward: string;
  addressDetail?: string;
  location?: {
    lat: number;
    lng: number;
  };
  title?: string;
  content: string;
  media: ReportMedia[];
  userId?: string | null;
  status: 'pending' | 'processing' | 'resolved' | 'rejected';
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

/**
 * Helper để đảm bảo URL luôn dùng HTTPS (trừ localhost)
 */
const ensureHttpsUrl = (url: string): string => {
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return url;
  }
  return url.replace(/^http:\/\//i, 'https://');
};

class ReportsService {
  private baseUrl: string;

  constructor() {
    // Sử dụng REPORTS_API_BASE_URL từ env.ts (đã normalize và đảm bảo HTTPS)
    // Thêm ensureHttpsUrl để double-check
    this.baseUrl = ensureHttpsUrl(REPORTS_API_BASE_URL);
    console.log('[ReportsService] Base URL:', this.baseUrl);
  }

  /**
   * Tạo một báo cáo mới
   */
  async createReport(data: CreateReportData): Promise<ApiResponse<Report>> {
    try {
      const response = await fetch(`${this.baseUrl}/reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to create report');
      }

      return result;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Lấy danh sách báo cáo
   */
  async getReports(options?: {
    limit?: number;
    skip?: number;
    status?: string;
    userId?: string;
  }): Promise<ApiResponse<Report[]>> {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', options.limit.toString());
      if (options?.skip) params.append('skip', options.skip.toString());
      if (options?.status) params.append('status', options.status);
      if (options?.userId) params.append('userId', options.userId);

      const queryString = params.toString();
      const url = `${this.baseUrl}/reports${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to fetch reports');
      }

      return result;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Lấy một báo cáo cụ thể theo ID
   */
  async getReportById(id: string): Promise<ApiResponse<Report>> {
    try {
      const response = await fetch(`${this.baseUrl}/reports/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || result.error || 'Failed to fetch report');
      }

      return result;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Convert file URI to base64 (for images/videos)
   */
  async convertUriToBase64(uri: string): Promise<string> {
    try {
      const response = await fetch(uri);
      const blob = await response.blob();
      
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64String = reader.result as string;
          // Remove data URL prefix (data:image/jpeg;base64,)
          const base64 = base64String.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    } catch (error) {
      throw error;
    }
  }

  /**
   * Prepare media files for upload
   * Converts blob URLs to base64 data URLs for storage
   */
  async prepareMediaFiles(
    media: Array<{ uri: string; type: 'image' | 'video' }>
  ): Promise<ReportMedia[]> {
    const preparedMedia: ReportMedia[] = [];

    for (const item of media) {
      try {
        let finalUri = item.uri;
        let filename = item.uri.split('/').pop() || `media.${item.type === 'video' ? 'mp4' : 'jpg'}`;

        // Check if it's a blob URL (blob:http://...)
        if (item.uri.startsWith('blob:')) {
          try {
            // Convert blob URL to base64 data URL
            const base64Data = await this.convertUriToBase64(item.uri);
            
            // Create data URL with proper MIME type
            const mimeType = item.type === 'video' 
              ? 'video/mp4' 
              : 'image/jpeg'; // Default to jpeg, could be improved to detect actual type
            
            finalUri = `data:${mimeType};base64,${base64Data}`;
            filename = `${filename}.${item.type === 'video' ? 'mp4' : 'jpg'}`;
          } catch (convertError) {
            // Fallback: keep original URI
          }
        } else if (item.uri.startsWith('data:')) {
          // Already a data URL, use as is
        } else if (item.uri.startsWith('http://') || item.uri.startsWith('https://')) {
          // HTTP URL, use as is (could be from cloud storage)
        } else {
          // File path or other, try to convert
          try {
            const base64Data = await this.convertUriToBase64(item.uri);
            const mimeType = item.type === 'video' ? 'video/mp4' : 'image/jpeg';
            finalUri = `data:${mimeType};base64,${base64Data}`;
            filename = `${filename}.${item.type === 'video' ? 'mp4' : 'jpg'}`;
          } catch (convertError) {
            // Skip conversion if it fails
          }
        }
        
        preparedMedia.push({
          uri: finalUri,
          type: item.type,
          filename: filename,
        });
      } catch (error) {
        // Skip this file but continue with others
      }
    }

    return preparedMedia;
  }

}

export default new ReportsService();

