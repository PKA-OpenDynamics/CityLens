// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import Constants from 'expo-constants';

// =============================================================================
// CORE API URL HELPERS
// =============================================================================

/**
 * Parse và làm sạch giá trị URL - loại bỏ key nếu có trong giá trị
 */
const parseUrlValue = (value: string | undefined): string | undefined => {
  if (!value) return undefined;
  
  // Nếu giá trị chứa dấu =, có thể là format "KEY=VALUE", chỉ lấy phần sau dấu =
  if (value.includes('=')) {
    const parts = value.split('=');
    if (parts.length > 1) {
      // Lấy phần cuối cùng sau dấu = (có thể có nhiều dấu = trong URL)
      const urlPart = parts.slice(1).join('=');
      return urlPart.trim();
    }
  }
  
  return value.trim();
};

/**
 * Đọc runtime config từ config.json (chỉ cho web)
 * Cho phép cập nhật API URL sau khi deploy mà không cần rebuild
 */
let runtimeConfig: { apiBaseUrl?: string } | null = null;

const loadRuntimeConfig = async (): Promise<{ apiBaseUrl?: string } | null> => {
  if (typeof window === 'undefined') return null;
  
  try {
    const response = await fetch('/config.json');
    if (response.ok) {
      const config = await response.json();
      return config;
    }
  } catch (error) {
    // Config file không tồn tại hoặc lỗi - không phải vấn đề nghiêm trọng
    console.log('[ENV] Runtime config.json not found, using build-time config');
  }
  
  return null;
};

/**
 * Đọc biến môi trường EXPO_PUBLIC_API_BASE_URL từ nhiều nguồn
 * Priority: 
 * 1. Runtime config (window.APP_CONFIG hoặc /config.json) - cho phép cập nhật sau deploy
 * 2. Expo Constants (build-time)
 * 3. process.env (build-time)
 * 4. localhost fallback
 */
const getRawApiBaseUrl = (): string => {
  // 1. Kiểm tra window.APP_CONFIG (manual override trong HTML)
  let fromRuntime: string | undefined;
  if (typeof window !== 'undefined') {
    const windowConfig = (window as any).APP_CONFIG;
    if (windowConfig?.apiBaseUrl) {
      fromRuntime = parseUrlValue(windowConfig.apiBaseUrl);
    }
    
    // 2. Kiểm tra runtime config đã load (sync check)
    if (!fromRuntime && runtimeConfig?.apiBaseUrl) {
      fromRuntime = parseUrlValue(runtimeConfig.apiBaseUrl);
    }
  }
  
  // 3. Build-time configs
  const fromConstantsRaw = (Constants.expoConfig?.extra as any)?.apiBaseUrl;
  const fromEnvRaw = typeof process !== 'undefined' ? process.env?.EXPO_PUBLIC_API_BASE_URL : undefined;
  const fallback = 'http://localhost:8000/api/v1';
  
  // Parse và làm sạch giá trị
  const fromConstants = parseUrlValue(fromConstantsRaw);
  const fromEnv = parseUrlValue(fromEnvRaw);
  
  // Priority: runtime > constants > env > fallback
  const result = fromRuntime || fromConstants || fromEnv || fallback;
  
  // Debug logging
  if (typeof window !== 'undefined') {
    console.log('[ENV Debug]', {
      fromRuntime,
      fromConstantsRaw,
      fromConstants,
      fromEnvRaw,
      fromEnv,
      fallback,
      result
    });
  }
  
  return result;
};

// Load runtime config khi module được import (chỉ cho web)
if (typeof window !== 'undefined') {
  loadRuntimeConfig().then(config => {
    runtimeConfig = config;
    if (config?.apiBaseUrl) {
      console.log('[ENV] Loaded runtime config:', config);
    }
  }).catch(() => {
    // Ignore errors
  });
}

/**
 * Giữ nguyên URL như được cấu hình (không tự động upgrade HTTPS)
 * LƯU Ý: Nếu trang chạy trên HTTPS, trình duyệt sẽ chặn các request HTTP (Mixed Content)
 * Để tránh lỗi, hãy cấu hình API URL là HTTPS từ đầu
 */
const ensureHttps = (url: string): string => {
  if (!url) return url;
  
  // Giữ nguyên URL như được cấu hình - không tự động upgrade
  // Nếu cần HTTPS, hãy cấu hình EXPO_PUBLIC_API_BASE_URL với HTTPS từ đầu
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
 * API Base URL - Đã normalize
 * Đây là nguồn duy nhất cho tất cả các API endpoints
 * 
 * LƯU Ý: Nếu trang chạy trên HTTPS, API URL cũng phải là HTTPS để tránh Mixed Content errors
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1
 * 
 * Hỗ trợ runtime config qua:
 * - window.APP_CONFIG.apiBaseUrl (set trong HTML trước khi load app)
 * - /config.json (file trong public folder)
 */
let _cachedApiBaseUrl: string | null = null;

const getApiBaseUrl = (): string => {
  // Cache để tránh tính toán lại mỗi lần gọi
  if (_cachedApiBaseUrl) {
    // Kiểm tra lại window.APP_CONFIG nếu có (có thể thay đổi động)
    if (typeof window !== 'undefined') {
      const windowConfig = (window as any).APP_CONFIG;
      if (windowConfig?.apiBaseUrl) {
        const runtimeUrl = parseUrlValue(windowConfig.apiBaseUrl);
        if (runtimeUrl) {
          _cachedApiBaseUrl = ensureHttps(normalizeApiBase(runtimeUrl));
          return _cachedApiBaseUrl;
        }
      }
    }
    return _cachedApiBaseUrl;
  }
  
  _cachedApiBaseUrl = ensureHttps(normalizeApiBase(getRawApiBaseUrl()));
  return _cachedApiBaseUrl;
};

// Export như một getter để có thể đọc runtime config
export const API_BASE_URL = getApiBaseUrl();

// Hàm helper để update runtime config (sau khi load config.json)
export const updateApiBaseUrl = (newUrl: string): void => {
  _cachedApiBaseUrl = ensureHttps(normalizeApiBase(newUrl));
  console.log('[ENV] Updated API_BASE_URL to:', _cachedApiBaseUrl);
};

// Log API URL khi khởi động (chỉ trên web để debug)
if (typeof window !== 'undefined') {
  console.log('[ENV] API_BASE_URL:', API_BASE_URL);
  console.log('[ENV] Raw API URL from env:', getRawApiBaseUrl());
  console.log('[ENV] To override API URL at runtime, set window.APP_CONFIG = { apiBaseUrl: "your-url" } before app loads');
  console.log('[ENV] Or place /config.json with: { "apiBaseUrl": "your-url" }');
}

// =============================================================================
// DERIVED API ENDPOINTS
// =============================================================================

/**
 * Helper để lấy API base URL hiện tại (có thể thay đổi runtime)
 */
const getCurrentApiBaseUrl = (): string => {
  // Kiểm tra window.APP_CONFIG trước (có thể thay đổi động)
  if (typeof window !== 'undefined') {
    const windowConfig = (window as any).APP_CONFIG;
    if (windowConfig?.apiBaseUrl) {
      const runtimeUrl = parseUrlValue(windowConfig.apiBaseUrl);
      if (runtimeUrl) {
        return ensureHttps(normalizeApiBase(runtimeUrl));
      }
    }
  }
  // Fallback về cached hoặc tính toán lại
  return _cachedApiBaseUrl || getApiBaseUrl();
};

/**
 * Weather API Base URL (không có /api/v1)
 * Dùng cho: weather, forecast realtime endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com
 */
export const WEATHER_API_BASE_URL = getCurrentApiBaseUrl().replace(/\/api\/v1$/, '');

/**
 * Reports API Base URL  
 * Dùng cho: /app/reports, /app/comments endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const REPORTS_API_BASE_URL = `${getCurrentApiBaseUrl()}/app`;

/**
 * Auth API Base URL
 * Dùng cho: /app/auth/login, /app/auth/register endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const AUTH_API_BASE_URL = REPORTS_API_BASE_URL;

/**
 * AI Chat API Base URL
 * Dùng cho: /ai/chat, /ai/history endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/ai
 */
export const AI_API_BASE_URL = `${getCurrentApiBaseUrl()}/ai`;

/**
 * Alerts API Base URL
 * Dùng cho: /app/alerts endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1/app
 */
export const ALERTS_API_BASE_URL = `${getCurrentApiBaseUrl()}/app`;

/**
 * Geographic API Base URL
 * Dùng cho: /geographic/buildings, /geographic/pois endpoints
 * Ví dụ: https://your-tunnel.trycloudflare.com/api/v1
 */
export const GEO_API_BASE_URL = getCurrentApiBaseUrl();

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

