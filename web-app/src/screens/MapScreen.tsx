// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

// Shared entry for MapScreen so TypeScript can resolve the module.
// React Native bundler sẽ tự chọn MapScreen.native.tsx (mobile) hoặc
// MapScreen.web.tsx (web) dựa trên platform.

export { default } from './MapScreen.native';









