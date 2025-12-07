## Cài đặt

```bash
cd citylens-app

# Cài dependency cơ bản
npm install

# React Navigation + icon
npm install @react-navigation/native \
  @react-navigation/bottom-tabs \
  @react-navigation/native-stack \
  @expo/vector-icons

# Native deps cho Expo
npx expo install react-native-screens react-native-safe-area-context expo-linear-gradient

# Bản đồ OSM (mobile)
npx expo install react-native-maps
```

## Chạy dự án

```bash
npx expo start
```