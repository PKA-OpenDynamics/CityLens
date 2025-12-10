// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Admin Service
 * Handles all admin-related API calls for dashboard, analytics, and alerts
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance with auth token
const createAuthAxios = () => {
  const token = localStorage.getItem('access_token');
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  });
};

export interface DashboardOverview {
  timestamp: string;
  user_statistics: {
    total: number;
    active: number;
    pending: number;
    suspended: number;
    by_role: Record<string, number>;
  };
  entity_statistics: {
    weather: { total: number; last_24h: number; last_7d: number };
    air_quality: { total: number; last_24h: number; last_7d: number };
    traffic: { total: number; last_24h: number; last_7d: number };
    parking: { total: number; available: number; occupied: number };
    civic_issues: { total: number; open: number; closed: number };
  };
  alert_statistics: {
    critical: number;
    high_priority_open: number;
  };
  system_health: {
    database: string;
    mongodb: string;
    status: string;
  };
}

export interface ActivityTimeline {
  period: string;
  start_date: string;
  end_date: string;
  timeline: Array<{
    date: string;
    weather: number;
    air_quality: number;
    traffic: number;
    civic_issues: number;
    total: number;
  }>;
}

export interface RealTimeMetrics {
  timestamp: string;
  weather: {
    latest: {
      temperature: number | null;
      humidity: number | null;
      description: string | null;
      observed_at: string | null;
    };
    hourly_average: { temperature: number | null };
  };
  air_quality: {
    latest: {
      aqi: number | null;
      pm25: number | null;
      pm10: number | null;
      observed_at: string | null;
    };
    hourly_average: { aqi: number | null };
  };
  traffic: {
    latest: {
      intensity: number | null;
      average_speed: number | null;
      observed_at: string | null;
    };
    hourly_average: { intensity: number | null };
  };
}

export interface Alert {
  id: string;
  type: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  description: string;
  location: string | null;
  timestamp: string;
  status: string;
  assigned_to: string | null;
  metadata: Record<string, any> | null;
}

export interface TrendData {
  period: string;
  district?: string;
  location?: string;
  data: Array<{
    date: string;
    [key: string]: any;
  }>;
}

export interface StatisticsSummary {
  period: string;
  generated_at: string;
  weather: any;
  air_quality: any;
  traffic: any;
  civic_issues: any;
  parking: any;
}

class AdminService {
  // ============ Dashboard APIs ============
  
  async getDashboardOverview(): Promise<DashboardOverview> {
    const api = createAuthAxios();
    const response = await api.get('/admin/dashboard/overview');
    return response.data;
  }

  async getActivityTimeline(days: number = 7): Promise<ActivityTimeline> {
    const api = createAuthAxios();
    const response = await api.get('/admin/dashboard/activity-timeline', {
      params: { days }
    });
    return response.data;
  }

  async getRealTimeMetrics(): Promise<RealTimeMetrics> {
    const api = createAuthAxios();
    const response = await api.get('/admin/dashboard/real-time-metrics');
    return response.data;
  }

  async getTopLocations(limit: number = 10, metric: 'traffic' | 'air_quality' | 'civic_issues' = 'traffic') {
    const api = createAuthAxios();
    const response = await api.get('/admin/dashboard/top-locations', {
      params: { limit, metric }
    });
    return response.data;
  }

  // ============ Analytics APIs ============
  
  async getWeatherTrends(days: number = 30, district?: string): Promise<TrendData> {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/trends/weather', {
      params: { days, district }
    });
    return response.data;
  }

  async getAirQualityTrends(days: number = 30, district?: string): Promise<TrendData> {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/trends/air-quality', {
      params: { days, district }
    });
    return response.data;
  }

  async getTrafficTrends(days: number = 7, location?: string) {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/trends/traffic', {
      params: { days, location }
    });
    return response.data;
  }

  async compareDistricts(metric: 'temperature' | 'aqi' | 'traffic_intensity', days: number = 7) {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/compare/districts', {
      params: { metric, days }
    });
    return response.data;
  }

  async exportDataCSV(entityType: 'weather' | 'air_quality' | 'traffic' | 'parking' | 'civic_issues', days: number = 7) {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/export/csv', {
      params: { entity_type: entityType, days },
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `citylens_${entityType}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    return true;
  }

  async getStatisticsSummary(days: number = 30): Promise<StatisticsSummary> {
    const api = createAuthAxios();
    const response = await api.get('/admin/analytics/statistics/summary', {
      params: { days }
    });
    return response.data;
  }

  // ============ Alert Management APIs ============
  
  async getActiveAlerts(severity?: 'info' | 'warning' | 'critical', limit: number = 50): Promise<Alert[]> {
    const api = createAuthAxios();
    const response = await api.get('/admin/alerts/active', {
      params: { severity, limit }
    });
    return response.data;
  }

  async getAlertHistory(days: number = 7, alertType?: string, severity?: string) {
    const api = createAuthAxios();
    const response = await api.get('/admin/alerts/history', {
      params: { days, alert_type: alertType, severity }
    });
    return response.data;
  }

  async acknowledgeAlert(alertId: string, notes?: string) {
    const api = createAuthAxios();
    const response = await api.post(`/admin/alerts/acknowledge/${alertId}`, { notes });
    return response.data;
  }

  async getAlertStatistics(days: number = 30) {
    const api = createAuthAxios();
    const response = await api.get('/admin/alerts/statistics', {
      params: { days }
    });
    return response.data;
  }

  async getAlertRecommendations() {
    const api = createAuthAxios();
    const response = await api.get('/admin/alerts/recommendations');
    return response.data;
  }

  // ============ User Management APIs (existing endpoints) ============
  
  async getPendingUsers() {
    const api = createAuthAxios();
    const response = await api.get('/admin/users/pending');
    return response.data;
  }

  async getAllUsers(status?: string, role?: string) {
    const api = createAuthAxios();
    const response = await api.get('/admin/users', {
      params: { status, role }
    });
    return response.data;
  }

  async approveUser(userId: string, approved: boolean, reason?: string) {
    const api = createAuthAxios();
    const response = await api.put(`/admin/users/${userId}/approve`, {
      approved,
      reason
    });
    return response.data;
  }

  async updateUserRole(userId: string, newRole: string) {
    const api = createAuthAxios();
    const response = await api.put(`/admin/users/${userId}/role`, {
      new_role: newRole
    });
    return response.data;
  }

  async suspendUser(userId: string, reason: string) {
    const api = createAuthAxios();
    const response = await api.post(`/admin/users/${userId}/suspend`, { reason });
    return response.data;
  }

  async getUserStats() {
    const api = createAuthAxios();
    const response = await api.get('/admin/stats');
    return response.data;
  }
}

// Export both the class and an instance for convenience
export const adminService = new AdminService();
export default AdminService;
