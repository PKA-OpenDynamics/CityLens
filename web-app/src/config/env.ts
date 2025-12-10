// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import Constants from 'expo-constants';

// =============================================================================
// CORE API URL HELPERS
// =============================================================================

/**
 * Đọc biến môi trường EXPO_PUBLIC_API_BASE_URL từ nhiều nguồn
 * Priority: 1. Expo Constants 2. process.env 3. localhost fallback
 */
const getRawApiBaseUrl = (): string => {
  return (
    (Constants.expoConfig?.extra as any)?.apiBaseUrl ||
    (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_API_BASE_URL) ||
    'http://localhost:8000/api/v1'
  );
};

/**
 * Tự động upgrade HTTP sang HTTPS cho production (Cloudflare Tunnels)
 * Giữ nguyên HTTP cho localhost development
 */
const ensureHttps = (url: string): string => {
  if (!url) return url;
  // Giữ nguyên HTTP cho localhost development
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return url;
  }
  // Upgrade HTTP sang HTTPS cho production (Cloudflare Tunnels luôn hỗ trợ HTTPS)
  if (url.startsWith('http://') && url.includes('.trycloudflare.com')) {
    return url.replace('http://', 'https://');
  }
  return url;
};

/**
 * Normalize API base URL - đảm bảo luôn kết thúc bằng /api/v1
 */
const normalizeApiBase = (base: string): string => {
  const trimmed = base.replace(/\/+$/, '');
  if (/\/api\/v1$/i.test(trimmed)) return trimmed;
  return `${trimmed}/api/v1`;
};

/**
 * API Base URL - Đã normalize và đảm bảo HTTPS cho production
 * Đây là nguồn duy nhất cho tất cả các API endpoints
 * 
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1
 */
export const API_BASE_URL = ensureHttps(normalizeApiBase(getRawApiBaseUrl()));

// =============================================================================
// DERIVED API ENDPOINTS
// =============================================================================

/**
 * Weather API Base URL (không có /api/v1)
 * Dùng cho: weather, forecast realtime endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com
 */
export const WEATHER_API_BASE_URL = API_BASE_URL.replace(/\/api\/v1$/, '');

/**
 * Reports API Base URL  
 * Dùng cho: /app/reports, /app/comments endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const REPORTS_API_BASE_URL = `${API_BASE_URL}/app`;

/**
 * Auth API Base URL
 * Dùng cho: /app/auth/login, /app/auth/register endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const AUTH_API_BASE_URL = REPORTS_API_BASE_URL;

/**
 * AI Chat API Base URL
 * Dùng cho: /app/ai/chat, /app/ai/history endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app/ai
 */
export const AI_API_BASE_URL = `${API_BASE_URL}/app/ai`;

/**
 * Alerts API Base URL
 * Dùng cho: /app/alerts endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const ALERTS_API_BASE_URL = `${API_BASE_URL}/app`;

/**
 * Geographic API Base URL
 * Dùng cho: /geographic/buildings, /geographic/pois endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1
 */
export const GEO_API_BASE_URL = API_BASE_URL;

// =============================================================================
// OTHER CONFIGS
// =============================================================================

/**
 * TomTom API Key
 */
export const TOMTOM_API_KEY =
  Constants.expoConfig?.extra?.tomtomApiKey ||
  (typeof process !== 'undefined' && process.env?.TOMTOM_API_KEY) ||
  '';

/**
 * MongoDB Atlas Connection String
 */
export const MONGODB_URI =
  (Constants.expoConfig?.extra as any)?.mongodbUri ||
  (typeof process !== 'undefined' && process.env?.MONGODB_URI) ||
  (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_MONGODB_URI) ||
  '';

/**
 * MongoDB Database Name
 */
export const MONGODB_DB_NAME =
  (Constants.expoConfig?.extra as any)?.mongodbDbName ||
  (typeof process !== 'undefined' && process.env?.MONGODB_DB_NAME) ||
  (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_MONGODB_DB_NAME) ||
  'citylens';

/**
 * Kiểm tra xem TomTom API key đã được cấu hình chưa
 */
export const isTomTomApiKeyConfigured = (): boolean => {
  return (
    TOMTOM_API_KEY !== '' &&
    TOMTOM_API_KEY !== 'YOUR_TOMTOM_API_KEY_HERE' &&
    TOMTOM_API_KEY.length >= 32
  );
};

// =============================================================================
// DEBUG HELPERS
// =============================================================================

/**
 * Log tất cả API URLs (chỉ dùng cho debug)
 */
export const logApiUrls = (): void => {
  if (typeof console !== 'undefined') {
    console.log('[ENV] API URLs:', {
      API_BASE_URL,
      WEATHER_API_BASE_URL,
      REPORTS_API_BASE_URL,
      AUTH_API_BASE_URL,
      AI_API_BASE_URL,
      ALERTS_API_BASE_URL,
      GEO_API_BASE_URL,
    });
  }
};

