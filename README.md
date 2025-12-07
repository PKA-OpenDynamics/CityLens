<p align="center">
  <img src="docs/assets/citylens-logo.png" alt="CityLens Logo" width="120">
</p>

<h1 align="center">CityLens</h1>

<p align="center">
  <strong>Nền tảng Thành phố Thông minh với Linked Open Data</strong>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  </a>
  <a href="https://github.com/PKA-Open-Dynamics/CityLens">
    <img src="https://img.shields.io/badge/GitHub-Repository-black.svg" alt="GitHub">
  </a>
  <a href="https://www.npmjs.com/org/pka_opendynamics_2025">
    <img src="https://img.shields.io/badge/npm-Packages-red.svg" alt="npm">
  </a>
</p>

---

## Mục lục

- [Ý tưởng bài toán](#ý-tưởng-bài-toán)
- [Giải pháp kỹ thuật](#giải-pháp-kỹ-thuật)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Tính năng chính](#tính-năng-chính)
- [Đóng góp nguồn dữ liệu mở](#đóng-góp-nguồn-dữ-liệu-mở)
- [NPM Packages](#npm-packages)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Công nghệ](#công-nghệ)
- [Cài đặt](#cài-đặt)
- [Tài liệu](#tài-liệu)
- [Giấy phép](#giấy-phép)

---

## Ý tưởng bài toán

### Vấn đề cần giải quyết

Các thành phố lớn tại Việt Nam đang đối mặt với nhiều thách thức trong quản lý đô thị:

1. **Thiếu kênh tiếp nhận hiệu quả**: Người dân khó khăn trong việc báo cáo các vấn đề hạ tầng đô thị (đèn đường hỏng, đường xuống cấp, rác thải...)

2. **Dữ liệu phân tán**: Thông tin về chất lượng không khí, giao thông, thời tiết nằm rải rác ở nhiều nguồn, thiếu tích hợp

3. **Không có chuẩn dữ liệu thống nhất**: Các hệ thống hiện tại không tuân theo chuẩn mở, gây khó khăn cho việc liên thông dữ liệu

4. **Thiếu minh bạch**: Người dân không thể theo dõi tiến độ xử lý các vấn đề đã báo cáo

### Đối tượng người dùng

| Đối tượng | Nhu cầu |
|-----------|---------|
| Công dân | Báo cáo sự cố, theo dõi tiến độ xử lý |
| Cơ quan quản lý | Tiếp nhận, phân loại và xử lý báo cáo |
| Nhà hoạch định | Phân tích dữ liệu đô thị để ra quyết định |
| Nhà phát triển | Truy cập API mở để xây dựng ứng dụng |

---

## Giải pháp kỹ thuật

### Tổng quan giải pháp

CityLens là nền tảng thành phố thông minh sử dụng kiến trúc Linked Open Data (LOD) 3 lớp, tuân thủ các chuẩn quốc tế NGSI-LD, SOSA/SSN và FiWARE Smart Data Models.

### Cách tiếp cận

```
┌─────────────────────────────────────────────────────────────┐
│                    CityLens Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│   │   Web App   │   │     Web     │   │  External   │       │
│   │   (React)   │   │  Dashboard  │   │    APIs     │       │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘       │
│          │                 │                 │              │
│          └────────────┬────┴─────────────────┘              │
│                       ▼                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            FastAPI Backend (REST + NGSI-LD)         │   │
│   └─────────────────────────────────────────────────────┘   │
│                       │                                     │
│          ┌────────────┼────────────┐                        │
│          ▼            ▼            ▼                        │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│   │PostgreSQL│  │ GraphDB  │  │  Redis   │                  │
│   │ +PostGIS │  │ (RDF/OWL)│  │ (Cache)  │                  │
│   └──────────┘  └──────────┘  └──────────┘                  │ 
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Điểm nổi bật của giải pháp

| Đặc điểm | Mô tả |
|----------|-------|
| **NGSI-LD Compliant** | API tuân thủ chuẩn ETSI NGSI-LD, tương thích với hệ sinh thái FiWARE |
| **Linked Open Data** | Dữ liệu liên kết với ontology chuẩn, có thể truy vấn SPARQL |
| **Spatial-enabled** | Tích hợp PostGIS cho các truy vấn không gian địa lý |
| **Real-time** | Cập nhật dữ liệu thời gian thực qua WebSocket |
| **Open Source** | Toàn bộ mã nguồn mở theo giấy phép GPL-3.0 |

---

## Kiến trúc hệ thống

### Kiến trúc 3 lớp dữ liệu (LOD Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Layer 3: DỮ LIỆU CÔNG DÂN (Citizen Data Layer)                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Báo cáo sự cố (CivicIssue)                               │   │
│  │  • Phản hồi và đánh giá                                     │   │
│  │  • Sự kiện thời gian thực                                   │   │
│  │  Storage: PostgreSQL + MongoDB                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │                                      │
│  Layer 2: HẠ TẦNG ĐÔ THỊ (Urban Infrastructure Layer)              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Dữ liệu cảm biến IoT (AQI, nhiệt độ, độ ẩm)             │   │
│  │  • Thông tin giao thông (TrafficFlowObserved)               │   │
│  │  • Cơ sở tiện ích công cộng (POIs)                         │   │
│  │  Storage: PostgreSQL + GraphDB (RDF)                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │                                      │
│  Layer 1: NỀN TẢNG ĐỊA LÝ (Geographic Foundation Layer)           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Ranh giới hành chính (Quận/Huyện, Phường/Xã)            │   │
│  │  • Mạng lưới đường phố                                      │   │
│  │  • Tòa nhà và công trình                                    │   │
│  │  Source: OpenStreetMap                                       │   │
│  │  Storage: PostgreSQL + PostGIS                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sơ đồ kiến trúc chi tiết

> **Lưu ý**: Sơ đồ kiến trúc chi tiết đang được cập nhật và sẽ được bổ sung trong phiên bản tiếp theo.
> 
> _Planned: System Architecture Diagram, Component Diagram, Deployment Diagram_

### Ontology và Data Models

CityLens sử dụng ontology tùy chỉnh kết hợp với các ontology chuẩn:

| Ontology | Mục đích | Namespace |
|----------|----------|-----------|
| CityLens Ontology | Định nghĩa riêng cho báo cáo công dân | `citylens:` |
| SOSA/SSN | Mô hình hóa cảm biến và quan sát | `sosa:` |
| GeoSPARQL | Dữ liệu không gian địa lý | `geo:` |
| Smart Data Models | Data models cho Smart City | `sdm:` |

---

## Tính năng chính

### Cho Công dân

- Báo cáo sự cố với hình ảnh và định vị GPS
- Theo dõi trạng thái xử lý báo cáo
- Xem bản đồ các vấn đề đô thị
- Nhận thông báo cập nhật

### Cho Cơ quan quản lý

- Dashboard quản lý báo cáo tập trung
- Phân loại và gán xử lý tự động
- Thống kê và báo cáo
- Quản lý người dùng và phân quyền

### Dữ liệu đô thị tích hợp

- Chất lượng không khí thời gian thực (AQI)
- Thông tin giao thông và tắc đường
- Dữ liệu thời tiết
- Ranh giới hành chính từ OpenStreetMap

---

## Đóng góp nguồn dữ liệu mở

### Dữ liệu đã xây dựng

| Loại dữ liệu | Mô tả | Định dạng |
|--------------|-------|-----------|
| Ranh giới hành chính Hà Nội | 30 quận/huyện, 579 phường/xã | GeoJSON, PostGIS |
| Danh mục báo cáo | 28 danh mục vấn đề đô thị | JSON |
| Ontology CityLens | Định nghĩa lớp và thuộc tính | OWL/Turtle |
| Context NGSI-LD | JSON-LD context cho entities | JSON-LD |

### NPM Packages đóng góp

Dự án phát hành 3 thư viện npm mã nguồn mở:

| Package | Mô tả | npm |
|---------|-------|-----|
| `@pka_opendynamics_2025/citylens-utils` | Tiện ích xử lý dữ liệu đô thị | [Link](https://www.npmjs.com/package/@pka_opendynamics_2025/citylens-utils) |
| `@pka_opendynamics_2025/citylens-geo-utils` | Xử lý dữ liệu địa lý và GeoJSON | [Link](https://www.npmjs.com/package/@pka_opendynamics_2025/citylens-geo-utils) |
| `@pka_opendynamics_2025/citylens-ngsi-ld` | Xây dựng NGSI-LD entities | [Link](https://www.npmjs.com/package/@pka_opendynamics_2025/citylens-ngsi-ld) |

### Nguồn dữ liệu tích hợp

| Nguồn | Loại dữ liệu | API |
|-------|--------------|-----|
| OpenStreetMap | Bản đồ nền, ranh giới | Overpass API |
| AQICN | Chất lượng không khí | REST API |
| OpenWeatherMap | Thời tiết | REST API |
| TomTom | Giao thông | Traffic API |

---

## NPM Packages

### citylens-utils

Thư viện tiện ích xử lý dữ liệu đô thị:

```typescript
import { calculateDistance, getAqiInfo, formatDateVi } from '@pka_opendynamics_2025/citylens-utils';

// Tính khoảng cách giữa 2 điểm
const distance = calculateDistance(21.0285, 105.8542, 21.0378, 105.8342);

// Lấy thông tin AQI
const aqiInfo = getAqiInfo(75);
console.log(aqiInfo.labelVi); // => 'Trung bình'
```

### citylens-geo-utils

Thư viện xử lý dữ liệu địa lý và GeoJSON:

```typescript
import { createPoint, distanceBetweenPoints, isInHanoi } from '@pka_opendynamics_2025/citylens-geo-utils';

// Tạo GeoJSON Point
const point = createPoint(21.0285, 105.8542);

// Kiểm tra điểm trong Hà Nội
console.log(isInHanoi(point)); // => true
```

### citylens-ngsi-ld

Thư viện xây dựng NGSI-LD entities theo chuẩn ETSI:

```typescript
import { createCivicIssue, createEntityId } from '@pka_opendynamics_2025/citylens-ngsi-ld';

// Tạo CivicIssue entity
const issue = createCivicIssue({
  id: 'report-001',
  title: 'Đèn đường hỏng',
  description: 'Đèn đường tại ngã tư không hoạt động',
  location: { lat: 21.0285, lon: 105.8542 },
  category: 'infrastructure',
});
```

---

## Cấu trúc dự án

```
CityLens/
├── backend/                    # FastAPI backend với LOD
│   ├── app/                    # Mã nguồn chính
│   │   ├── api/               # API endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── graphdb/               # Ontology và RDF
│   ├── scripts/               # Scripts tiện ích
│   └── setup.sh               # Script cài đặt
│
├── web-dashboard/             # Next.js TypeScript dashboard
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   └── setup.sh              # Script cài đặt
│
├── mobile-app/                # Flutter mobile app
│   └── lib/
│       └── features/         # Feature modules
│
├── packages/                  # NPM packages
│   ├── citylens-utils/       # Tiện ích chung
│   ├── citylens-geo-utils/   # Xử lý địa lý
│   └── citylens-ngsi-ld/     # NGSI-LD builder
│
├── docs/                      # Tài liệu dự án
├── LICENSE                    # GPL-3.0 License
├── CONTRIBUTING.md            # Hướng dẫn đóng góp
└── CODE_OF_CONDUCT.md         # Quy tắc ứng xử
```

---

## Công nghệ

### Backend

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Framework | FastAPI | 0.109.0 |
| Database | PostgreSQL + PostGIS | 15+ |
| Graph Database | Apache Jena Fuseki | 4.x |
| Cache | Redis | 7+ |
| API Standards | REST, NGSI-LD | v1 |

### Web Dashboard

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Framework | Next.js | 14.2 |
| Language | TypeScript | 5.6 |
| Styling | Tailwind CSS | 3.4 |
| Maps | Leaflet | 1.9 |

### Mobile App

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Framework | Flutter | 3.x |
| Language | Dart | 3.x |
| Platform | iOS, Android | - |

---

## Cài đặt

### Yêu cầu hệ thống

- Python 3.11 trở lên
- Node.js 20 trở lên
- PostgreSQL 15+ với PostGIS
- Redis 7+ (tùy chọn)

### Backend

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### Web Dashboard

```bash
cd web-dashboard
chmod +x setup.sh
./setup.sh
```

### Mobile App

```bash
cd mobile-app
flutter pub get
flutter run
```

### Docker (Khuyến nghị)

```bash
docker-compose up -d
```

---

## Tài liệu

### Tài liệu dự án

| Tài liệu | Mô tả |
|----------|-------|
| [CHANGELOG.md](CHANGELOG.md) | Lịch sử thay đổi |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Hướng dẫn đóng góp |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Quy tắc ứng xử |

### Tài liệu sub-projects

| Sub-project | README | DEPENDENCIES | CHANGELOG |
|-------------|--------|--------------|-----------|
| Backend | [README](backend/README.md) | [DEPENDENCIES](backend/DEPENDENCIES.md) | [CHANGELOG](backend/CHANGELOG.md) |
| Web Dashboard | [README](web-dashboard/README.md) | [DEPENDENCIES](web-dashboard/DEPENDENCIES.md) | [CHANGELOG](web-dashboard/CHANGELOG.md) |
| Mobile App | [README](mobile-app/README.md) | - | - |

### NPM Packages

| Package | README |
|---------|--------|
| citylens-utils | [README](packages/citylens-utils/README.md) |
| citylens-geo-utils | [README](packages/citylens-geo-utils/README.md) |
| citylens-ngsi-ld | [README](packages/citylens-ngsi-ld/README.md) |

### API Documentation

| Tài liệu | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/api/v1/docs |
| ReDoc | http://localhost:8000/api/v1/redoc |

---

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng đọc:

- [Hướng dẫn đóng góp](CONTRIBUTING.md)
- [Quy tắc ứng xử](CODE_OF_CONDUCT.md)

---

## Giấy phép

Dự án này được phát hành dưới giấy phép **GNU General Public License v3.0 (GPL-3.0)**.

```
Copyright (c) 2025 CityLens Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

Xem file [LICENSE](LICENSE) để biết chi tiết.

---

## Liên hệ

| Kênh | Liên kết |
|------|----------|
| Bug Reports | [GitHub Issues](https://github.com/PKA-Open-Dynamics/CityLens/issues) |
| Discussions | [GitHub Discussions](https://github.com/PKA-Open-Dynamics/CityLens/discussions) |
| Repository | https://github.com/PKA-Open-Dynamics/CityLens |

---

## Tác giả

**CityLens Contributors** - Team PKA Open Dynamics

---

<p align="center">
  <strong>CityLens</strong> - Smart City Platform with Linked Open Data<br>
</p>
