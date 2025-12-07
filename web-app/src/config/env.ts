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
 */
export const WEATHER_API_BASE_URL =
  (Constants.expoConfig?.extra as any)?.weatherApiBaseUrl ||
  (typeof process !== 'undefined' && process.env?.WEATHER_API_BASE_URL) ||
  'http://localhost:8000';

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

