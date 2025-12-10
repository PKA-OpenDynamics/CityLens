// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import Constants from 'expo-constants';

/**
 * Lấy TomTom API Key từ environment variables
 * Key được cấu hình trong file .env và truyền qua app.config.js
 * Trên web, có thể đọc trực tiếp từ process.env nếu expo-constants không hoạt động
 */
export const TOMTOM_API_KEY =
  Constants.expoConfig?.extra?.tomtomApiKey ||
  (typeof process !== 'undefined' && process.env?.TOMTOM_API_KEY) ||
  '';

/**
 * API base URL cho backend (weather/forecast realtime)
 * Tự động derive từ EXPO_PUBLIC_API_BASE_URL bằng cách bỏ /api/v1
 * 
 * Production: Chỉ cần set EXPO_PUBLIC_API_BASE_URL=https://your-tunnel.trycloudflare.com/api/v1
 * Local Development: http://localhost:8000
 */
const getApiBaseUrl = () => {
  const apiUrl = 
    (Constants.expoConfig?.extra as any)?.apiBaseUrl ||
    (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_API_BASE_URL) ||
    'http://localhost:8000/api/v1';
  // Remove /api/v1 to get base URL
  return apiUrl.replace(/\/api\/v1$/, '');
};

export const WEATHER_API_BASE_URL = getApiBaseUrl();

/**
 * MongoDB Atlas Connection String
 */
export const MONGODB_URI =
  (Constants.expoConfig?.extra as any)?.mongodbUri ||
  (typeof process !== 'undefined' && process.env?.MONGODB_URI) ||
  process.env?.EXPO_PUBLIC_MONGODB_URI ||
  '';

/**
 * MongoDB Database Name
 */
export const MONGODB_DB_NAME =
  (Constants.expoConfig?.extra as any)?.mongodbDbName ||
  (typeof process !== 'undefined' && process.env?.MONGODB_DB_NAME) ||
  process.env?.EXPO_PUBLIC_MONGODB_DB_NAME ||
  'citylens';

/**
 * API Base URL for Reports (Backend API)
 * Tự động derive từ EXPO_PUBLIC_API_BASE_URL + /app
 * 
 * Production: Chỉ cần set EXPO_PUBLIC_API_BASE_URL
 * Local Development: http://localhost:8000/api/v1/app
 */
const getReportsApiBaseUrl = () => {
  const apiUrl = 
    (Constants.expoConfig?.extra as any)?.apiBaseUrl ||
    (typeof process !== 'undefined' && process.env?.EXPO_PUBLIC_API_BASE_URL) ||
    'http://localhost:8000/api/v1';
  return `${apiUrl}/app`;
};

export const REPORTS_API_BASE_URL = getReportsApiBaseUrl();

/**
 * API Base URL for Authentication (Backend API)
 * Tự động derive từ EXPO_PUBLIC_API_BASE_URL + /app
 * 
 * Production: Chỉ cần set EXPO_PUBLIC_API_BASE_URL
 * Local Development: http://localhost:8000/api/v1/app
 */
export const AUTH_API_BASE_URL = REPORTS_API_BASE_URL; // Same as reports

/**
 * Kiểm tra xem API key đã được cấu hình chưa
 */
export const isTomTomApiKeyConfigured = (): boolean => {
  return (
    TOMTOM_API_KEY !== '' &&
    TOMTOM_API_KEY !== 'YOUR_TOMTOM_API_KEY_HERE' &&
    TOMTOM_API_KEY.length >= 32
  );
};

