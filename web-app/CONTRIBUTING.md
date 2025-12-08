# Hướng dẫn Đóng góp cho CityLens Web App

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án CityLens Web App! Tài liệu này cung cấp hướng dẫn để đóng góp vào ứng dụng mobile.

## Mục lục

- [Quy tắc ứng xử](#quy-tắc-ứng-xử)
- [Thiết lập môi trường](#thiết-lập-môi-trường)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Chuẩn code](#chuẩn-code)
- [Quy trình Pull Request](#quy-trình-pull-request)

## Quy tắc ứng xử

Dự án này tuân theo [Quy tắc ứng xử](../CODE_OF_CONDUCT.md) của CityLens.

## Thiết lập môi trường

### Yêu cầu

- Node.js 20+
- npm 10+
- Expo CLI (sẽ được cài tự động)
- Backend API đang chạy

### Cài đặt

```bash
# Clone repository
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/web-app

# Cài đặt dependencies
npm install

# Copy và cấu hình environment
cp .env.example .env
# Chỉnh sửa .env với API URL của bạn

# Chạy development server
npm start
```

### Chạy trên các nền tảng

```bash
# Web
npm run web

# Android (yêu cầu Android Studio/Emulator)
npm run android

# iOS (yêu cầu macOS và Xcode)
npm run ios
```

## Cấu trúc dự án

```
web-app/
├── src/
│   ├── components/       # Reusable components
│   │   ├── Avatar.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── FloatingAIButton.tsx
│   │   └── ReportCard.tsx
│   ├── config/           # Configuration
│   │   └── env.ts
│   ├── contexts/         # React Context
│   │   └── AuthContext.tsx
│   ├── navigation/       # Navigation setup
│   │   └── RootNavigator.tsx
│   ├── screens/          # App screens
│   │   ├── LoginScreen.tsx
│   │   ├── ExploreScreen.native.tsx
│   │   ├── MapScreen.native.tsx
│   │   ├── ReportScreen.native.tsx
│   │   └── ProfileScreen.native.tsx
│   └── services/         # API services
│       ├── auth.ts
│       ├── weather.ts
│       └── traffic.ts
├── assets/               # Static assets
├── App.tsx               # Entry point
└── app.json              # Expo configuration
```

## Chuẩn code

### TypeScript Style

- **ESLint**: Tuân thủ ESLint rules
- **Prettier**: Sử dụng Prettier formatter
- **Type safety**: Luôn sử dụng TypeScript types
- **Naming**: PascalCase cho components, camelCase cho functions

### Component Guidelines

```typescript
// ✅ Good: Functional component với TypeScript
interface Props {
  title: string;
  onPress: () => void;
}

export const MyComponent: React.FC<Props> = ({ title, onPress }) => {
  return <TouchableOpacity onPress={onPress}>...</TouchableOpacity>;
};

// ❌ Bad: Không có type definitions
export const MyComponent = ({ title, onPress }) => {
  return <TouchableOpacity onPress={onPress}>...</TouchableOpacity>;
};
```

### File Naming

- **Components**: PascalCase (`Avatar.tsx`, `ReportCard.tsx`)
- **Services**: camelCase (`auth.ts`, `weather.ts`)
- **Screens**: PascalCase với suffix Screen (`LoginScreen.tsx`)
- **Platform-specific**: Thêm `.native` hoặc `.web` (`MapScreen.native.tsx`)

### Git Commits

Sử dụng [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: thêm tính năng upload ảnh cho báo cáo
fix: sửa lỗi crash khi mở map
docs: cập nhật README với hướng dẫn build
style: format code với prettier
refactor: tổ chức lại structure của services
test: thêm unit tests cho auth service
```

## Quy trình Pull Request

### 1. Fork và Clone

```bash
# Fork repo trên GitHub, sau đó clone
git clone https://github.com/YOUR_USERNAME/CityLens.git
cd CityLens/web-app
```

### 2. Tạo Branch

```bash
# Tạo branch từ develop
git checkout develop
git checkout -b feature/ten-tinh-nang

# Hoặc cho bugfix
git checkout -b fix/ten-loi
```

### 3. Development

- Viết code tuân theo chuẩn
- Test trên ít nhất 2 platforms (web + 1 mobile)
- Thêm/cập nhật documentation nếu cần
- Commit với message rõ ràng

### 4. Testing

```bash
# Test trên web
npm run web

# Test trên Android/iOS
npm run android
npm run ios

# Check TypeScript
npx tsc --noEmit

# Check linting
npm run lint
```

### 5. Push và Create PR

```bash
git push origin feature/ten-tinh-nang
```

Sau đó tạo Pull Request trên GitHub:

- **Base**: `develop`
- **Title**: Mô tả ngắn gọn thay đổi
- **Description**: Chi tiết về:
  - Vấn đề được giải quyết
  - Cách giải quyết
  - Testing đã thực hiện
  - Screenshots (nếu có UI changes)

### Template Pull Request

```markdown
## Mô tả

Mô tả ngắn gọn về thay đổi.

## Loại thay đổi

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Đã test trên Web
- [ ] Đã test trên Android
- [ ] Đã test trên iOS
- [ ] TypeScript compile thành công
- [ ] Không có linting errors

## Screenshots

Nếu có UI changes, thêm screenshots.
```

## Báo lỗi

Khi báo lỗi, vui lòng bao gồm:

- **Mô tả chi tiết** về lỗi
- **Các bước tái hiện** lỗi
- **Platform**: Web/iOS/Android
- **Device/Browser**: Thông tin thiết bị
- **Screenshots/Videos**: Nếu có
- **Logs**: Console logs hoặc error messages

## Đề xuất tính năng

Khi đề xuất tính năng mới:

- **Mô tả** tính năng rõ ràng
- **Use case**: Tại sao cần tính năng này
- **Mockups**: UI mockups nếu có
- **Alternatives**: Các giải pháp thay thế đã xem xét

## Câu hỏi?

Nếu có câu hỏi, liên hệ qua:

- GitHub Issues: https://github.com/PKA-OpenDynamics/CityLens/issues
- Email: contributors@citylens.org

---

Cảm ơn bạn đã đóng góp cho CityLens! 🎉
