# CityLens Mobile App

Ứng dụng di động CityLens cho người dân tham gia báo cáo và theo dõi tình hình thành phố.

## Công nghệ

- **Framework**: Flutter 3.16+
- **Language**: Dart 3.2+
- **State Management**: Riverpod
- **Maps**: Google Maps Flutter
- **Network**: Dio + Retrofit
- **Local Storage**: Hive

## Cài đặt

### Yêu cầu hệ thống

- Flutter SDK 3.16 hoặc cao hơn
- Dart SDK 3.2 hoặc cao hơn
- Android Studio / Xcode (cho iOS)

### Cài đặt từ mã nguồn

```bash
# Di chuyển đến thư mục
cd mobile-app

# Cài đặt dependencies
flutter pub get

# Chạy code generation
flutter pub run build_runner build --delete-conflicting-outputs

# Chạy ứng dụng
flutter run
```

## Build APK/IPA

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## Cấu trúc thư mục

```
mobile-app/
├── lib/
│   ├── core/              # Core utilities
│   │   ├── constants/
│   │   ├── network/
│   │   └── theme/
│   ├── features/          # Feature modules
│   │   ├── auth/
│   │   ├── map/
│   │   ├── report/
│   │   └── profile/
│   └── main.dart          # Entry point
├── assets/                # Images, fonts
└── pubspec.yaml           # Dependencies
```

## Tính năng chính

- Xem bản đồ sự cố thời gian thực
- Báo cáo sự cố với ảnh/video
- Nhận cảnh báo theo vị trí
- Theo dõi điểm và huy hiệu
- Xếp hạng người đóng góp

## License

MIT License - xem file [LICENSE](../LICENSE)
