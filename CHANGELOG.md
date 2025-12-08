# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi quan trọng của dự án CityLens được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Chưa phát hành]

### Dự kiến
- Mobile app triển khai đầy đủ
- Phân tích nâng cao với machine learning
- Hỗ trợ đa ngôn ngữ (i18n)
- Push notifications

## [1.0.0] - 2025-12-07

### Thêm mới

#### Backend (v1.0.0)
- API NGSI-LD tuân thủ chuẩn ETSI
- Hỗ trợ ontology SOSA/SSN
- API dữ liệu địa lý với PostGIS
- Tích hợp LOD (OpenWeatherMap, AQICN, TomTom, OSM)
- Xác thực người dùng với JWT
- Hệ thống quản lý báo cáo
- Quản lý ranh giới hành chính

#### Web Dashboard (v2.1.0)
- IntegratedDataPanel cho hiển thị LOD
- BoundarySelector cho truy vấn địa lý
- Hiển thị dữ liệu đa nguồn (thời tiết, AQI, giao thông, OSM)
- Dashboard với analytics
- Trang dữ liệu địa lý

#### Tài liệu
- README đầy đủ cho tất cả sub-projects
- DEPENDENCIES.md với thông tin license
- Hướng dẫn CONTRIBUTING.md
- CHANGELOG.md theo định dạng Keep a Changelog
- License headers GPL-3.0 trong tất cả source files

#### Hạ tầng
- Cấu hình Docker Compose
- Thiết lập PostgreSQL + PostGIS
- Alembic migrations
- Mẫu cấu hình environment
- Scripts cài đặt tự động (setup.sh)

### Thay đổi
- Thống nhất license GPL-3.0 cho tất cả components
- Dọn sạch code và scripts không dùng
- Chuẩn hóa API client với hỗ trợ PATCH
- Cập nhật cấu trúc tài liệu

## 2025-11-25

### Thêm mới
- SQLAlchemy models cho tất cả entities
- Alembic migration framework
- Script import OSM với osmium
- Seeding categories báo cáo
- Neo4j/GraphDB ontology schema

### Thay đổi
- Cập nhật Python dependencies cho Python 3.11
- Đổi tên `metadata` thành `report_metadata` trong Report model

### Sửa lỗi
- Import và export models
- Cấu hình Alembic
- Xử lý geometry PostGIS

### Bảo mật
- Thêm .gitignore rules cho:
  - Dữ liệu OSM lớn (*.osm.pbf, *.geojson)
  - Cấu hình environment (.env)
  - Database files

## 2025-11-20

### Thêm mới
- Cấu trúc dự án ban đầu
- Skeleton API backend với FastAPI
- Nền tảng web dashboard với React + TypeScript
- Thiết lập mobile app với Flutter
- Authentication models
- Report submission models
- Thiết kế database schema
- Cấu hình Docker cho development
- Thiết lập CI/CD pipeline
- Tài liệu dự án

### Hạ tầng
- Thiết lập PostgreSQL database
- MongoDB cho dữ liệu thời gian thực
- Neo4j knowledge graph foundation
- Redis cho caching
- Cấu hình môi trường development

---

## Phân loại thay đổi

- **Thêm mới** - Tính năng mới
- **Thay đổi** - Thay đổi trong chức năng hiện có
- **Loại bỏ** - Tính năng sắp bị gỡ bỏ
- **Xóa bỏ** - Tính năng đã bị gỡ bỏ
- **Sửa lỗi** - Sửa lỗi
- **Bảo mật** - Thay đổi liên quan đến bảo mật

---

[Chưa phát hành]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.2.0...v1.0.0

