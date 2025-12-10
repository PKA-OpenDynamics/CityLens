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
 * Chỉ cần base URL (ví dụ: http://localhost:8000)
 * Code sẽ tự thêm /api/v1 nếu chưa có
 * 
 * Production (Cloudflare Tunnel): https://rooms-tools-kirk-nelson.trycloudflare.com
 * Local Development: http://localhost:8000
 */
export const WEATHER_API_BASE_URL =
  (Constants.expoConfig?.extra as any)?.weatherApiBaseUrl ||
  (typeof process !== 'undefined' && process.env?.WEATHER_API_BASE_URL) ||
  'https://rooms-tools-kirk-nelson.trycloudflare.com';

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
 * Now using FastAPI backend at /api/v1/app/reports
 * 
 * Production (Cloudflare Tunnel): https://rooms-tools-kirk-nelson.trycloudflare.com/api/v1/app
 * Local Development: http://localhost:8000/api/v1/app
 */
export const REPORTS_API_BASE_URL =
  (Constants.expoConfig?.extra as any)?.reportsApiBaseUrl ||
  (typeof process !== 'undefined' && process.env?.REPORTS_API_BASE_URL) ||
  process.env?.EXPO_PUBLIC_REPORTS_API_BASE_URL ||
  'https://rooms-tools-kirk-nelson.trycloudflare.com/api/v1/app';

/**
 * API Base URL for Authentication (Backend API)
 * Now using FastAPI backend at /api/v1/app/auth
 * 
 * Production (Cloudflare Tunnel): https://rooms-tools-kirk-nelson.trycloudflare.com/api/v1/app
 * Local Development: http://localhost:8000/api/v1/app
 */
export const AUTH_API_BASE_URL =
  (Constants.expoConfig?.extra as any)?.authApiBaseUrl ||
  (typeof process !== 'undefined' && process.env?.AUTH_API_BASE_URL) ||
  process.env?.EXPO_PUBLIC_AUTH_API_BASE_URL ||
  'https://rooms-tools-kirk-nelson.trycloudflare.com/api/v1/app';

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

