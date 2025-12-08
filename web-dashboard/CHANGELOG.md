# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi quan trọng của CityLens Web Dashboard được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Chưa phát hành]

### Dự kiến
- Theo dõi trạng thái báo cáo trực quan
- Hệ thống thông báo người dùng
- Tùy chọn lọc nâng cao

## [1.0.0] - 2025-12-07

### Thêm mới
- IntegratedDataPanel - Hiển thị dữ liệu LOD toàn diện
  - Section OpenStreetMap (boundaries, POIs, streets)
  - Section thời tiết từ OpenWeatherMap
  - Section chỉ số chất lượng không khí từ AQICN
  - Section lưu lượng giao thông từ TomTom
  - Khả năng làm mới dữ liệu thời gian thực

- BoundarySelector - Trình duyệt chọn boundaries
  - Chọn theo cấp bậc quận/phường
  - Chức năng tìm kiếm
  - Hiển thị thống kê nhanh

- DEPENDENCIES.md - Tài liệu dependencies đầy đủ
  - Tất cả các gói npm với licenses
  - Thông tin phiên bản
  - Ghi chú tương thích license

- setup.sh - Script cài đặt tự động

### Thay đổi
- Dọn sạch dự án
  - Xóa components không dùng (charts/, ui/)
  - Xóa utilities không dùng (types/, utils/)
  - Hợp nhất các file API
  - Cập nhật index exports

### Sửa lỗi
- Trang Reports placeholder
- API client patch method
- Lỗi build sau dọn dẹp

## 2025-12-05

### Thêm mới
- Tích hợp NGSI-LD API - Hỗ trợ đầy đủ chuẩn ETSI NGSI-LD
  - Service ngsi-ld-api.ts với các API methods
  - Hỗ trợ ontology SOSA/SSN (Sensors, Observations)
  - Triển khai FiWARE Smart Data Models
    - AirQualityObserved
    - WeatherObserved
    - TrafficFlowObserved
    - OffStreetParking
    - Streetlight
    - WaterQualityObserved
  - Hỗ trợ Geo-queries (near, within)

- Entity Browser Page - Quản lý NGSI-LD entity
  - Duyệt tất cả entities với lọc theo type
  - Tìm kiếm nâng cao theo ID và type
  - JSON-LD viewer cho chi tiết entity
  - Thống kê thời gian thực

- Data Catalog Page - Danh mục nguồn dữ liệu mở
  - 6 nguồn dữ liệu tích hợp
  - Thống kê entity theo type
  - Giám sát trạng thái nguồn dữ liệu

- API Integration Page - Tài liệu API tương tác
  - 4 ví dụ API với nhiều ngôn ngữ (cURL, JavaScript, Python)
  - Chức năng copy-to-clipboard
  - Ví dụ code trực tiếp

### Thay đổi
- Thống nhất license thành GPL-3.0
- API Client - Thêm hỗ trợ PATCH method
- Kiến trúc - Chuyển sang Next.js 14 App Router

### Xóa bỏ
- Các trang chưa hoàn thiện (ai-assistant, timeline-explorer, v.v.)

### Sửa lỗi
- ENV variable prefix (VITE_* -> NEXT_PUBLIC_*)
- Xung đột license MIT và GPL-3.0
- Lỗi TypeScript trong API client

## 2025-11-24

### Thêm mới
- Phát hành bản đầu
- Dashboard cơ bản với reports, facilities, analytics
- Hiển thị bản đồ với Leaflet
- Quản lý báo cáo
- Quản lý người dùng
- Hệ thống xác thực
- Tích hợp REST API

---

[Chưa phát hành]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/PKA-Open-Dynamics/CityLens/releases/tag/v1.0.0
