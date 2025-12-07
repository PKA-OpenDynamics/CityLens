<p align="center">
  <img src="../docs/assets/citylens-logo.png" alt="CityLens Logo" width="120">
</p>

<h1 align="center">CityLens Web Dashboard</h1>

<p align="center">
  <strong>Admin Dashboard cho Smart City Platform</strong>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  </a>
  <img src="https://img.shields.io/badge/Next.js-14-black.svg" alt="Next.js">
  <img src="https://img.shields.io/badge/TypeScript-5-blue.svg" alt="TypeScript">
</p>

---

## Tổng quan

CityLens Web Dashboard là giao diện quản trị viên cho phép:
- Xem và quản lý báo cáo từ người dân
- Hiển thị dữ liệu địa lý từ OpenStreetMap
- Tích hợp dữ liệu LOD từ nhiều nguồn (weather, AQI, traffic)
- Theo dõi thống kê và analytics
- Quản lý người dùng và cài đặt

## Công nghệ

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Framework | Next.js (App Router) | 14.2.33 |
| Language | TypeScript | 5.6.3 |
| Styling | Tailwind CSS | 3.4.15 |
| Maps | Leaflet + React Leaflet | 1.9.4 |
| Charts | Recharts | 2.14.1 |
| State | Zustand | 5.0.2 |
| HTTP | Axios | 1.7.9 |

## Cài đặt từ mã nguồn

### Yêu cầu hệ thống

- Node.js 20 trở lên
- npm 10 trở lên
- Backend API đang chạy (http://localhost:8000)

### Cài đặt tự động

```bash
chmod +x setup.sh
./setup.sh
```

### Cài đặt thủ công

**Bước 1: Clone repository**

```bash
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/web-dashboard
```

**Bước 2: Cài đặt dependencies**

```bash
npm install
```

**Bước 3: Cấu hình environment**

```bash
cp .env.example .env.local
# Chỉnh sửa .env.local nếu cần thay đổi API URL
```

**Bước 4: Chạy development server**

```bash
npm run dev
```

Ứng dụng sẽ chạy tại: **http://localhost:3000**

## Build cho production

```bash
# Build application
npm run build

# Start production server
npm start
```

## Chạy với Docker

```bash
# Build image
docker build -t citylens-web-dashboard .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1 \
  citylens-web-dashboard
```

## Cấu trúc thư mục

```
web-dashboard/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (dashboard)/        # Dashboard layout group
│   │   │   ├── dashboard/      # Main dashboard
│   │   │   ├── geographic/     # Dữ liệu địa lý
│   │   │   ├── reports/        # Quản lý báo cáo
│   │   │   ├── users/          # Quản lý người dùng
│   │   │   └── settings/       # Cài đặt
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing/redirect
│   ├── components/             # React components
│   │   ├── geographic/         # LOD data panels
│   │   ├── layout/             # Header, sidebar
│   │   ├── map/                # Map components
│   │   └── providers/          # Context providers
│   └── lib/                    # Utilities
│       ├── api.ts              # API services
│       ├── api-client.ts       # HTTP client
│       └── utils.ts            # Helpers
├── public/                     # Static assets
├── setup.sh                    # Script cài đặt
├── CHANGELOG.md                # Lịch sử thay đổi
├── CONTRIBUTING.md             # Hướng dẫn đóng góp
├── DEPENDENCIES.md             # Thông tin thư viện
├── LICENSE                     # GPL-3.0 License
└── package.json                # npm dependencies
```

## Tính năng chính

### Dashboard
- Thống kê tổng quan (reports, users, facilities)
- Recent activities
- Quick actions

### Geographic Data
- Interactive map với Leaflet
- Boundary selector (quận, phường)
- Tích hợp dữ liệu LOD:
  - Weather (OpenWeatherMap)
  - Air Quality (AQICN)
  - Traffic (TomTom)
  - Geographic (OpenStreetMap)

### Reports Management
- Danh sách báo cáo từ người dân
- Filter theo status, category
- Chi tiết báo cáo với location

## Development

```bash
# Development server
npm run dev

# Lint code
npm run lint

# Format code
npm run format

# Type check
npx tsc --noEmit

# Build
npm run build
```

## Đóng góp

Xem [CONTRIBUTING.md](CONTRIBUTING.md) để biết cách đóng góp cho dự án.

## Giấy phép

Dự án này được phát hành theo giấy phép **GNU General Public License v3.0 (GPL-3.0)**.

```
Copyright (c) 2025 CityLens Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

Xem file [LICENSE](LICENSE) để biết chi tiết.

## Tài liệu liên quan

- [DEPENDENCIES.md](DEPENDENCIES.md) - Danh sách thư viện
- [CHANGELOG.md](CHANGELOG.md) - Lịch sử thay đổi
- [Backend README](../backend/README.md) - Backend API documentation
- [Main README](../README.md) - Tài liệu dự án chính
