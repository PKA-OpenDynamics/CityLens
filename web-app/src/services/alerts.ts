// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { ALERTS_API_BASE_URL } from '../config/env';

/**
 * Helper để đảm bảo URL luôn dùng HTTPS (trừ localhost)
 */
const ensureHttpsUrl = (url: string): string => {
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return url;
  }
  return url.replace(/^http:\/\//i, 'https://');
};

// Sử dụng ALERTS_API_BASE_URL từ env.ts (đã normalize và đảm bảo HTTPS)
const API_BASE = ensureHttpsUrl(ALERTS_API_BASE_URL);

export type AlertItem = {
  _id: string;
  type?: string;
  severity?: string;
  title: string;
  description?: string;
  ward?: string;
  recommendation?: string;
  impact?: string;
  affectedPopulation?: string;
  isAIGenerated?: boolean;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
};

class AlertsService {
  async list(): Promise<AlertItem[]> {
    const base = API_BASE.replace(/\/$/, '');
    const urls = [
      `${base}/alerts`, // Primary: /api/v1/app/alerts
    ];

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      try {
        const res = await fetch(url);
        if (res.status === 404) {
          // try next URL silently
          continue;
        }
        if (!res.ok) {
          // Nếu không phải URL cuối cùng, thử tiếp
          if (i < urls.length - 1) continue;
          throw new Error(`Alerts API error: ${res.status}`);
        }
        const data = await res.json();
        // Backend returns { success: true, data: [...], count: N }
        if (Array.isArray(data)) return data;
        if (Array.isArray(data?.data)) return data.data;
        if (Array.isArray(data?.items)) return data.items;
        return [];
      } catch (err) {
        // Nếu là URL cuối cùng và không phải 404, ném lỗi
        if (i === urls.length - 1) {
          console.warn('[AlertsService] All endpoints failed, returning empty array', err);
          return [];
        }
        // Tiếp tục thử URL tiếp theo
      }
    }

    return [];
  }
}

export const alertsService = new AlertsService();

