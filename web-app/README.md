# CityLens Web App

Ứng dụng web cho hệ thống thành phố thông minh CityLens - cung cấp thông tin thời tiết, chất lượng không khí, giao thông và phản ánh hiện trường.

## 📱 Giới thiệu

CityLens Web App là ứng dụng React Native được xây dựng với Expo, hỗ trợ chạy trên web, iOS và Android. Ứng dụng cho phép người dùng:
- Xem thông tin thời tiết và chất lượng không khí theo thời gian thực
- Theo dõi tình trạng giao thông
- Phản ánh các vấn đề hiện trường (xả rác, lấn chiếm, v.v.)
- Tương tác với AI Assistant để tìm kiếm thông tin
- Quản lý hồ sơ cá nhân

## 🛠️ Công nghệ

- **Framework**: React Native với Expo
- **Language**: TypeScript
- **Navigation**: React Navigation
- **State Management**: React Context API
- **Maps**: React Native Maps
- **UI Components**: Expo Vector Icons, Linear Gradient
- **Build Tool**: Expo CLI

## 📋 Yêu cầu hệ thống

### Tối thiểu
- **Node.js**: 18.x trở lên
- **npm**: 9.x trở lên (hoặc yarn/pnpm)
- **Git**: Để clone repository

### Khuyến nghị
- **Node.js**: 20.x LTS
- **npm**: 10.x
- **RAM**: Tối thiểu 4GB
- **Disk**: Tối thiểu 2GB trống

### Platform Support
- ✅ Web (Chrome, Firefox, Safari, Edge)
- ✅ iOS (qua Expo Go hoặc build native)
- ✅ Android (qua Expo Go hoặc build native)

## 🚀 Cài đặt nhanh

### Cách 1: Sử dụng setup script (Khuyến nghị)

#### Linux/Mac:
```bash
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/web-app
chmod +x scripts/*.sh
./scripts/setup.sh
```

#### Windows PowerShell:
```powershell
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens\web-app
.\scripts\setup.ps1
```

### Cách 2: Cài đặt thủ công

```bash
# 1. Clone repository
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/web-app

# 2. Cài đặt dependencies
npm install

# 3. Tạo file .env
cp .env.example .env
# Hoặc tạo thủ công:
echo "EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" > .env

# 4. Chạy ứng dụng
npm start
```

## 🔨 Build từ mã nguồn

### Development Build

#### Web (Khuyến nghị cho development)
```bash
# Cách 1: Sử dụng script
./scripts/start.sh        # Linux/Mac
.\scripts\start.ps1       # Windows

# Cách 2: Sử dụng npm
npm start
# Sau đó chọn 'w' để mở web browser
```

#### Android
```bash
npm run android
# Hoặc
npx expo start --android
```

#### iOS
```bash
npm run ios
# Hoặc
npx expo start --ios
```

### Production Build

#### Web Production Build
```bash
# Cách 1: Sử dụng script
./scripts/build.sh        # Linux/Mac
.\scripts\build.ps1       # Windows

# Cách 2: Sử dụng npm
npm run build:web
# Output sẽ ở thư mục 'web-build/'
```

#### Android APK
```bash
# Cần cài đặt EAS CLI trước
npm install -g eas-cli

# Build APK
eas build --platform android --profile production
```

#### iOS IPA
```bash
# Cần cài đặt EAS CLI và Apple Developer account
eas build --platform ios --profile production
```

## 📁 Cấu trúc thư mục

```
web-app/
├── src/
│   ├── components/          # React components tái sử dụng
│   │   ├── Avatar.tsx
│   │   ├── FloatingAIButton.tsx
│   │   └── ReportCard.tsx
│   ├── config/              # Cấu hình ứng dụng
│   │   └── env.ts           # Environment variables
│   ├── contexts/            # React Context providers
│   │   └── AuthContext.tsx   # Authentication context
│   ├── navigation/          # Navigation configuration
│   │   └── RootNavigator.tsx # Root navigation setup
│   ├── screens/             # Màn hình ứng dụng
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── ExploreScreen.native.tsx
│   │   ├── MapScreen.native.tsx
│   │   ├── ReportScreen.native.tsx
│   │   ├── ProfileScreen.native.tsx
│   │   └── ...
│   └── services/            # API services
│       ├── auth.ts          # Authentication API
│       ├── weather.ts       # Weather & AQI API
│       └── traffic.ts       # Traffic API
├── assets/                  # Static assets
│   ├── icon.png
│   ├── splash-icon.png
│   └── videos/
├── scripts/                 # Build & setup scripts
│   ├── setup.sh            # Setup script (Linux/Mac)
│   ├── setup.ps1           # Setup script (Windows)
│   ├── start.sh            # Start script (Linux/Mac)
│   ├── start.ps1           # Start script (Windows)
│   ├── build.sh            # Build script (Linux/Mac)
│   └── build.ps1           # Build script (Windows)
├── App.tsx                  # Application entry point
├── app.json                 # Expo configuration
├── app.config.js            # Expo config (JavaScript)
├── package.json             # Dependencies & scripts
├── tsconfig.json            # TypeScript configuration
├── .env.example             # Environment variables template
├── LICENSE                  # GNU GPL-3.0 License
├── CHANGELOG.md             # Changelog
└── README.md                # Tài liệu này
```

## 🔧 Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục `web-app/`:

```env
# API Base URL
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Hoặc nếu backend chạy trên server khác:
# EXPO_PUBLIC_API_BASE_URL=https://api.citylens.example.com/api/v1
```

**Lưu ý**: 
- File `.env` không được commit vào git (đã có trong .gitignore)
- Sử dụng `.env.example` làm template
- Biến môi trường phải bắt đầu với `EXPO_PUBLIC_` để được expose ra client

### Expo Configuration

File `app.json` chứa cấu hình Expo:
- App name, version, slug
- Icon, splash screen
- Platform-specific settings (iOS, Android, Web)
- Orientation, permissions

## 📦 Dependencies

### Runtime Dependencies
- `expo`: Expo SDK framework
- `react` & `react-native`: Core React Native framework
- `@react-navigation/*`: Navigation library
- `expo-linear-gradient`: UI gradients
- `react-native-maps`: Maps integration
- `@react-native-async-storage/async-storage`: Local storage
- `expo-image-picker`: Image picker functionality

### Development Dependencies
- `typescript`: Type checking
- `@types/react`: TypeScript types for React
- `@types/react-native`: TypeScript types for React Native

Xem `package.json` để biết danh sách đầy đủ và versions.

## 📝 Available Scripts

### Development
- `npm start`: Khởi động Expo development server
- `npm run android`: Chạy trên Android emulator/device
- `npm run ios`: Chạy trên iOS simulator/device
- `npm run web`: Chạy trên web browser

### Build
- `npm run build:web`: Build production cho web
- `npm run build:android`: Build APK cho Android (cần EAS)
- `npm run build:ios`: Build IPA cho iOS (cần EAS)

### Utilities
- `npm run setup`: Chạy setup script (tương đương ./scripts/setup.sh)

## 🧪 Testing

```bash
# Chạy tests (nếu có)
npm test

# Chạy tests với coverage
npm run test:coverage
```

## 🐛 Bug Tracker

Báo lỗi và đề xuất tính năng tại: 
**https://github.com/PKA-Open-Dynamics/CityLens/issues**

## 📄 License

Dự án này được cấp phép theo **GNU General Public License v3.0 (GPL-3.0)**.

Xem file [LICENSE](LICENSE) để biết toàn văn giấy phép.

### Copyright Notice

```
Copyright (C) 2025 CityLens Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

## 👥 Contributors

CityLens Contributors - PKA Open Dynamics

## 📚 Tài liệu tham khảo

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🔗 Liên kết

- **Repository**: https://github.com/PKA-Open-Dynamics/CityLens
- **Backend API**: Xem [backend/README.md](../backend/README.md)
- **Issues**: https://github.com/PKA-Open-Dynamics/CityLens/issues
- **Releases**: https://github.com/PKA-Open-Dynamics/CityLens/releases

## 🆘 Troubleshooting

### Lỗi "Module not found"
```bash
# Xóa node_modules và cài lại
rm -rf node_modules package-lock.json
npm install
```

### Lỗi "Port already in use"
```bash
# Đổi port
npx expo start --port 8082
```

### Lỗi "Cannot connect to API"
- Kiểm tra backend đã chạy chưa
- Kiểm tra `EXPO_PUBLIC_API_BASE_URL` trong file `.env`
- Kiểm tra CORS settings trong backend

### Build fails
```bash
# Clear cache
npx expo start -c
# Hoặc
rm -rf .expo node_modules
npm install
```

## 📊 Changelog

Xem [CHANGELOG.md](CHANGELOG.md) để biết lịch sử thay đổi chi tiết.
