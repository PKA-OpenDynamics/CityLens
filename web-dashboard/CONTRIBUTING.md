# Hướng dẫn Đóng góp cho CityLens Web Dashboard

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án CityLens Web Dashboard! Tài liệu này cung cấp hướng dẫn để đóng góp vào web dashboard.

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
- Backend API đang chạy (http://localhost:8000)

### Cài đặt

```bash
# Clone repository
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/web-dashboard

# Cài đặt dependencies
npm install

# Copy và cấu hình environment
cp .env.example .env.local
# Chỉnh sửa .env.local nếu cần

# Chạy development server
npm run dev
```

Ứng dụng sẽ chạy tại: http://localhost:3000

## Cấu trúc dự án

```
web-dashboard/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (dashboard)/        # Dashboard layout group
│   │   │   ├── dashboard/      # Main dashboard page
│   │   │   ├── geographic/     # Geographic data page
│   │   │   ├── reports/        # Reports page
│   │   │   ├── users/          # Users page
│   │   │   └── settings/       # Settings page
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing page
│   ├── components/             # React components
│   │   ├── geographic/         # Geographic components
│   │   ├── layout/             # Layout components
│   │   ├── map/                # Map components
│   │   └── providers/          # Context providers
│   └── lib/                    # Utilities & API
│       ├── api.ts              # API services
│       ├── api-client.ts       # HTTP client
│       └── utils.ts            # Utility functions
├── public/                     # Static files
└── package.json                # Dependencies
```

## Chuẩn code

### TypeScript Style

- **Strict mode**: TypeScript strict enabled
- **ESLint**: Sử dụng eslint-config-next
- **Prettier**: Auto-format with Tailwind plugin

### Format code

```bash
# Lint
npm run lint

# Format
npm run format
```

### License Header

Mỗi file TypeScript/TSX phải có license header:

```typescript
// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)
```

### Component Conventions

- Functional components với TypeScript
- Use `'use client'` directive cho client components
- Tailwind CSS cho styling
- Lucide React cho icons

### Folder Naming

- `kebab-case` cho folders
- `PascalCase.tsx` cho components
- `camelCase.ts` cho utilities

## Quy trình Pull Request

1. Fork repository
2. Tạo branch: `git checkout -b feature/ten-tinh-nang`
3. Commit changes: `git commit -m "feat: mô tả"`
4. Push branch: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

### Commit Message Format

```
type(scope): description

[optional body]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Build & Test

```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Liên hệ

- Issues: [GitHub Issues](https://github.com/PKA-Open-Dynamics/CityLens/issues)
- Email: citylens@example.com
