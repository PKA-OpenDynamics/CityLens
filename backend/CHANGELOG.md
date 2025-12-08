# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi quan trọng của CityLens Backend được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Chưa phát hành]

### Dự kiến
- Hỗ trợ WebSocket cho thông báo thời gian thực
- Phân tích nâng cao với machine learning
- Hỗ trợ đa ngôn ngữ (i18n)

## [1.0.0] - 2025-12-07

### Thêm mới

#### Tích hợp LOD (Linked Open Data)
- API NGSI-LD tuân thủ chuẩn ETSI
- Hỗ trợ ontology SOSA/SSN cho dữ liệu cảm biến
- API dữ liệu địa lý với PostGIS
- Tích hợp các nguồn LOD bên ngoài:
  - OpenWeatherMap (dữ liệu thời tiết)
  - AQICN (chỉ số chất lượng không khí)
  - TomTom (lưu lượng giao thông)
  - OpenStreetMap (ranh giới địa lý, POIs)

#### Tính năng chính
- Xác thực người dùng với JWT tokens
- Hệ thống quản lý báo cáo (CRUD)
- Quản lý ranh giới hành chính (quận, phường)
- Dữ liệu đường phố và tòa nhà từ OSM
- Endpoints tổng hợp dữ liệu thời gian thực

#### Cơ sở dữ liệu
- PostgreSQL 15+ với extension PostGIS
- SQLAlchemy 2.0 ORM với hỗ trợ async
- Alembic migrations cho quản lý schema
- Hỗ trợ MongoDB cho sự kiện thời gian thực
- Lớp cache Redis

#### API Endpoints
- `/api/v1/auth/` - Xác thực
- `/api/v1/users/` - Quản lý người dùng
- `/api/v1/reports/` - Báo cáo công dân
- `/api/v1/geographic/` - Dữ liệu địa lý
- `/api/v1/statistics/` - Thống kê
- `/ngsi-ld/v1/` - Entities tuân thủ NGSI-LD

#### Tài liệu
- Tài liệu OpenAPI/Swagger
- Tài liệu ReDoc
- README đầy đủ
- DEPENDENCIES.md với thông tin license
- Hướng dẫn CONTRIBUTING

### Bảo mật
- Mã hóa mật khẩu với bcrypt
- Xác thực JWT token
- Cấu hình CORS
- Kiểm tra đầu vào với Pydantic

## 2025-12-01

### Thêm mới
- API endpoints địa lý cho boundaries
- Scripts import dữ liệu OSM
- Tổng hợp dữ liệu đô thị
- Hỗ trợ truy vấn nhiều boundaries

### Thay đổi
- Cập nhật dependencies cho Python 3.11
- Cải thiện xử lý lỗi trong adapters

### Sửa lỗi
- Xử lý geometry PostGIS trong export GeoJSON
- Đơn giản hóa boundary cho các polygon lớn

## 2025-11-25

### Thêm mới
- SQLAlchemy models cho tất cả entities
- Alembic migration framework
- Script import OSM với osmium
- Seeding categories báo cáo
- Neo4j/GraphDB ontology schema

### Thay đổi
- Cập nhật Python dependencies
- Đổi tên `metadata` thành `report_metadata` trong Report model

### Sửa lỗi
- Import và export models
- Cấu hình Alembic

## 2025-11-15

### Thêm mới
- Cấu trúc dự án FastAPI ban đầu
- Các thao tác CRUD cơ bản
- Thiết lập database PostgreSQL
- Cấu hình Docker
- Xác thực cơ bản

---

[Chưa phát hành]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.3.0...v1.0.0
[0.3.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/PKA-Open-Dynamics/CityLens/releases/tag/v0.1.0
