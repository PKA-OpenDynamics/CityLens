// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

/**
 * Report Service
 */

import { apiClient } from './api';
import { Report, ReportStatus } from '@/types/api';

export const reportService = {
  async getReports(params?: {
    skip?: number;
    limit?: number;
    status?: ReportStatus;
  }): Promise<Report[]> {
    return apiClient.get<Report[]>('/reports', params);
  },

  async getReportById(id: number): Promise<Report> {
    return apiClient.get<Report>(`/reports/${id}`);
  },

  async getNearbyReports(params: {
    lat: number;
    lng: number;
    radius?: number;
  }): Promise<Report[]> {
    return apiClient.get<Report[]>('/reports/nearby', params);
  },

  async verifyReport(id: number, status: ReportStatus): Promise<Report> {
    return apiClient.put<Report>(`/admin/reports/${id}/verify`, { status });
  },

  async getStatistics() {
    return apiClient.get('/admin/reports/stats');
  },
};
