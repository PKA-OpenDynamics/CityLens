// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

require('dotenv').config();

module.exports = {
  expo: {
    name: 'web-app',
    slug: 'web-app',
    version: '1.0.0',
    orientation: 'portrait',
    icon: './assets/icon.png',
    userInterfaceStyle: 'light',
    newArchEnabled: true,
    splash: {
      image: './assets/splash-icon.png',
      resizeMode: 'contain',
      backgroundColor: '#ffffff',
    },
    ios: {
      supportsTablet: true,
    },
    android: {
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#ffffff',
      },
      edgeToEdgeEnabled: true,
      predictiveBackGestureEnabled: false,
    },
    web: {
      favicon: './assets/logo.jpg',
    },
    extra: {
      // Only need one API base URL, all others are derived automatically
      apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      tomtomApiKey: process.env.TOMTOM_API_KEY || '',
      mongodbUri: process.env.MONGODB_URI || '',
      mongodbDbName: process.env.MONGODB_DB_NAME || 'citylens',
    },
  },
};


