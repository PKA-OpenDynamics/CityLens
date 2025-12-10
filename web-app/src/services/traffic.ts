// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { API_BASE_URL } from '../config/env';

/**
 * Helper để đảm bảo URL luôn dùng HTTPS (trừ localhost)
 */
const ensureHttpsUrl = (url: string): string => {
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return url;
  }
  return url.replace(/^http:\/\//i, 'https://');
};

// Sử dụng API_BASE_URL từ env.ts và đảm bảo HTTPS
const BASE_URL = ensureHttpsUrl(API_BASE_URL);

export type TrafficFlowResponse = {
  current_speed: number;
  free_flow_speed: number;
  current_travel_time: number;
  free_flow_travel_time: number;
  confidence: number;
  status: 'thông_thoáng' | 'trung_bình' | 'chậm' | 'tắc_nghẽn' | 'không_xác_định';
  status_vi: string;
  speed_ratio: number | null;
  coordinates: Array<{ latitude: number; longitude: number }>;
};

async function get<T>(path: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
  if (!BASE_URL) {
    throw new Error('API_BASE_URL chưa được cấu hình');
  }

  // Đảm bảo path có leading slash
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(BASE_URL + normalizedPath);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    });
  }
  const res = await fetch(url.toString());
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchTrafficFlow(lat: number, lon: number): Promise<TrafficFlowResponse> {
  return get<TrafficFlowResponse>('/traffic/flow', { lat, lon });
}

export async function fetchTrafficFlowByLocation(locationId: string): Promise<TrafficFlowResponse> {
  return get<TrafficFlowResponse>(`/traffic/flow/by-location/${locationId}`);
}

