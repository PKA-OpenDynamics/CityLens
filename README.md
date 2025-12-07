# CityLens

Ứng dụng Thành phố Thông minh sử dụng Linked Open Data, NGSI-LD và SOSA/SSN

## Giới thiệu

CityLens là nền tảng thành phố thông minh cho phép người dân báo cáo các vấn đề đô thị và cơ quan quản lý theo dõi, xử lý hiệu quả. Dự án sử dụng các tiêu chuẩn mở như NGSI-LD, SOSA/SSN và FiWARE Smart Data Models.

## Tính năng chính

- Báo cáo sự cố từ người dân với hình ảnh và vị trí
- Quản lý và xử lý báo cáo cho cơ quan chức năng
- Tích hợp dữ liệu cảm biến IoT (AQI, thời tiết, giao thông)
- Bản đồ tương tác hiển thị sự kiện thời gian thực
- API NGSI-LD chuẩn quốc tế
- Linked Open Data với GraphDB và SPARQL
- Ứng dụng di động và web dashboard

## Công nghệ

### Backend
- FastAPI với Python 3.11+
- PostgreSQL 15+ với PostGIS (dữ liệu có cấu trúc)
- Apache Jena Fuseki (Linked Open Data, SPARQL)
- MongoDB 7+ (sự kiện thời gian thực)
- Redis 7+ (cache và task queue)

### Web Dashboard
- React 18 với TypeScript
- Material-UI components
- Leaflet maps (100% miễn phí)
- Vite build tool

### Mobile App
- Flutter 3.x
- Dart 3.x
- Cross-platform (iOS & Android)

## Cấu trúc dự án

```
CityLens/
├── backend/              # FastAPI backend với LOD
├── web-dashboard/        # React TypeScript dashboard
├── mobile-app/          # Flutter mobile app
├── CityLens_Docs/       # Tài liệu chi tiết
├── LICENSE              # GPL-3.0 License
├── CONTRIBUTING.md      # Hướng dẫn đóng góp
└── CODE_OF_CONDUCT.md   # Quy tắc ứng xử
```

## Cài đặt nhanh

### Yêu cầu hệ thống

- Python 3.11 trở lên
- Node.js 18 trở lên
- PostgreSQL 15+ với PostGIS
- Redis 7+
- MongoDB 7+
- Apache Jena Fuseki hoặc GraphDB

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Chỉnh sửa .env với cấu hình của bạn
alembic upgrade head
uvicorn app.main:app --reload
```

### Web Dashboard

```bash
cd web-dashboard
npm install
cp .env.example .env
# Chỉnh sửa .env với cấu hình của bạn
npm run dev
```

### Mobile App

```bash
cd mobile-app
flutter pub get
flutter run
```

## Tài liệu

- Hướng dẫn cài đặt chi tiết: `CityLens_Docs/DATABASE_SETUP.md`
- Thiết kế database: `CityLens_Docs/DATABASE_DESIGN.md`
- Triển khai LOD: `docs/lod/LOD_IMPLEMENTATION_GUIDE.md`
- API Documentation: http://localhost:8000/docs (sau khi chạy backend)

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng đọc:

- [Hướng dẫn đóng góp](CONTRIBUTING.md)
- [Quy tắc ứng xử](CODE_OF_CONDUCT.md)

## Giấy phép

Dự án này được phát hành dưới giấy phép GNU General Public License v3.0 (GPL-3.0). Xem file [LICENSE](LICENSE) để biết chi tiết.

## Liên hệ

- GitHub Issues: Báo cáo lỗi và đề xuất tính năng
- GitHub Discussions: Thảo luận và hỏi đáp

## Tác giả

CityLens Contributors

## Trạng thái dự án

Phiên bản hiện tại: v0.2.0
Trạng thái: Đang phát triển tích cực

---

Được phát triển cho cuộc thi Olympic Tin học Sinh viên 2025
