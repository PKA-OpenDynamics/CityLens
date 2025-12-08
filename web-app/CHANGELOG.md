# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi quan trọng của CityLens Web App được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Chưa phát hành]

### Dự kiến
- Tích hợp đầy đủ AI Assistant
- Push notifications cho báo cáo
- Chế độ offline
- Hỗ trợ đa ngôn ngữ (i18n)

## [1.0.1] - 2025-12-08

### Tài liệu
- Cập nhật CHANGELOG.md với format tiếng Việt
- Thêm CONTRIBUTING.md với hướng dẫn đóng góp đầy đủ
- Thêm DEPENDENCIES.md với thông tin licenses

### Cải thiện
- Chuẩn hóa cấu trúc tài liệu
- Đồng bộ README format với các sub-projects khác

## [1.0.0] - 2025-12-07

### Thêm mới

#### Core Features
- Ứng dụng React Native với Expo
- Hỗ trợ đa nền tảng (Web, iOS, Android)
- Navigation với React Navigation v7
- Authentication với JWT
- State management với React Context API

#### Screens
- **Authentication**: Login, Register, Forgot Password, Change Password
- **Explore**: Trang chủ với weather, AQI, traffic data
- **Map**: Interactive map với location tracking
- **Reports**: Danh sách, chi tiết và tạo báo cáo mới
- **Profile**: Quản lý thông tin cá nhân và settings

#### Components
- Avatar component với fallback
- FloatingAIButton cho quick access
- ReportCard cho hiển thị reports
- ErrorBoundary cho error handling

#### Services
- Auth service với token management
- Weather & AQI service
- Traffic service
- API client với axios

### Technical Stack
- **Framework**: React Native 0.76.5
- **SDK**: Expo 52
- **Language**: TypeScript 5.3.3
- **Navigation**: React Navigation 7.x
- **Maps**: React Native Maps
- **Storage**: AsyncStorage

### Platform Support
- Web (Chrome, Firefox, Safari, Edge)
- iOS (via Expo Go hoặc native build)
- Android (via Expo Go hoặc native build)

### Thay đổi
- Cải thiện UI/UX với responsive design
- Tối ưu performance cho mobile
- Chuẩn hóa code structure
- Type safety với TypeScript

---

Để biết thêm chi tiết, xem [GitHub Releases](https://github.com/PKA-OpenDynamics/CityLens/releases).
- TypeScript support
- React Navigation for routing
- Expo Linear Gradient for UI
- React Native Maps for map functionality

## [Unreleased]

### Planned
- Enhanced map features
- More detailed reporting capabilities
- Social features
- Push notifications
- Offline mode support

