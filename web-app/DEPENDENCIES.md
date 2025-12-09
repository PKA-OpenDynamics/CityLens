# CityLens Web App - Dependencies

Tài liệu này liệt kê tất cả các thư viện và gói phần mềm được sử dụng trong dự án CityLens Web App.

## Phiên bản Runtime

- **Node.js**: 20+ (khuyến nghị 20.x LTS)
- **npm**: 10+

## Thư viện chính

### Core Framework

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Expo](https://expo.dev/) | ~52.0.32 | MIT | Development platform cho React Native |
| [React](https://react.dev/) | 18.3.1 | MIT | UI library |
| [React Native](https://reactnative.dev/) | 0.76.5 | MIT | Framework để build native apps |

### Navigation

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [@react-navigation/native](https://reactnavigation.org/) | ^7.0.13 | MIT | Navigation library |
| [@react-navigation/bottom-tabs](https://reactnavigation.org/) | ^7.2.0 | MIT | Bottom tab navigator |
| [@react-navigation/native-stack](https://reactnavigation.org/) | ^7.3.3 | MIT | Native stack navigator |
| [react-native-screens](https://github.com/software-mansion/react-native-screens) | ~4.4.0 | MIT | Native navigation primitives |
| [react-native-safe-area-context](https://github.com/th3rdwave/react-native-safe-area-context) | 4.12.0 | MIT | Safe area utilities |

### UI Components

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [@expo/vector-icons](https://icons.expo.fyi/) | ^14.0.4 | MIT | Icon library |
| [expo-linear-gradient](https://docs.expo.dev/versions/latest/sdk/linear-gradient/) | ~14.0.1 | MIT | Gradient components |
| [react-native-gesture-handler](https://docs.swmansion.com/react-native-gesture-handler/) | ~2.20.2 | MIT | Gesture handling |

### Maps & Location

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [react-native-maps](https://github.com/react-native-maps/react-native-maps) | ^1.18.0 | MIT | Maps component |
| [expo-location](https://docs.expo.dev/versions/latest/sdk/location/) | ~18.0.4 | MIT | Location services |

### Storage & Data

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [@react-native-async-storage/async-storage](https://react-native-async-storage.github.io/async-storage/) | 2.1.0 | MIT | Local storage |
| [axios](https://axios-http.com/) | ^1.7.9 | MIT | HTTP client |

### Media & Camera

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [expo-image-picker](https://docs.expo.dev/versions/latest/sdk/imagepicker/) | ~16.0.3 | MIT | Image picker |
| [expo-av](https://docs.expo.dev/versions/latest/sdk/av/) | ~15.0.1 | MIT | Audio/Video player |

### Development

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [TypeScript](https://www.typescriptlang.org/) | ~5.3.3 | Apache-2.0 | Type checking |
| [@types/react](https://www.npmjs.com/package/@types/react) | ~18.3.12 | MIT | React type definitions |
| [@types/react-native](https://www.npmjs.com/package/@types/react-native) | Latest | MIT | React Native types |

## Platform-specific Dependencies

### iOS

- CocoaPods (quản lý dependencies)
- Xcode 15+ (để build)

### Android

- Android Studio (để build)
- Gradle 8+ (build system)

## Build Tools

| Tool | Phiên bản | Mục đích |
|------|-----------|----------|
| [EAS Build](https://docs.expo.dev/build/introduction/) | Latest | Cloud build service |
| [Metro](https://facebook.github.io/metro/) | Latest | JavaScript bundler |

## Thư viện Optional

Các thư viện có thể được thêm trong tương lai:

- **Redux**: State management nâng cao
- **React Query**: Data fetching và caching
- **Formik**: Form management
- **Yup**: Schema validation
- **i18next**: Internationalization

## License Compliance

### Tổng quan Licenses

- **MIT**: Phần lớn dependencies (≈95%)
- **Apache-2.0**: TypeScript và một số libraries
- **BSD**: Một số core React Native modules

### License Tổng hợp

Tất cả dependencies đều sử dụng licenses tương thích với GPL-3.0:

- ✅ MIT License: Compatible
- ✅ Apache-2.0: Compatible
- ✅ BSD-3-Clause: Compatible

## Cập nhật Dependencies

### Kiểm tra updates

```bash
npm outdated
```

### Update dependencies

```bash
# Update minor/patch versions
npm update

# Update specific package
npm install expo@latest

# Update Expo SDK
npx expo install --fix
```

### Version Policy

- **Major updates**: Sau khi testing kỹ lưỡng
- **Minor updates**: Monthly
- **Patch updates**: As needed (security fixes)

## Security

### Kiểm tra vulnerabilities

```bash
npm audit
npm audit fix
```

### Báo cáo security issues

Email: security@citylens.org

## Thông tin thêm

### Package Registry

- NPM Registry: https://registry.npmjs.org/
- Expo Registry: https://registry.expo.dev/

### Documentation

- Expo Docs: https://docs.expo.dev/
- React Native Docs: https://reactnative.dev/docs/getting-started
- React Navigation: https://reactnavigation.org/docs/getting-started

---

**Lưu ý**: Luôn kiểm tra file `package.json` để biết phiên bản chính xác đang được sử dụng.
