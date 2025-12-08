# CityLens Backend - Hướng dẫn Import Database

Hướng dẫn import database với 487,000+ OpenStreetMap entities vào CityLens Backend.

---

## Yêu cầu

- Backend đang chạy (đã chạy `./start.sh`)
- Database dump file (`.sql`)
- PostgreSQL container đang hoạt động

---

## Cách 1: Import từ file SQL dump

### Bước 1: Chuẩn bị file dump

Nếu bạn chưa có file dump, liên hệ team để nhận:
- File: `citylens_dump.sql`
- Dung lượng: khoảng 50-100MB
- Chứa: 487,000+ OSM entities (buildings, roads, POIs)

### Bước 2: Import vào database

```bash
# Import trực tiếp vào container đang chạy
docker exec -i citylens-postgres psql -U citylens -d citylens_db < citylens_dump.sql
```

### Bước 3: Kiểm tra

```bash
# Kiểm tra số lượng entities
docker exec citylens-postgres psql -U citylens -d citylens_db -c "SELECT COUNT(*) FROM osm_entities;"

# Xem breakdown theo type
docker exec citylens-postgres psql -U citylens -d citylens_db -c "SELECT entity_type, COUNT(*) FROM osm_entities GROUP BY entity_type;"
```

---

## Cách 2: Import từ OpenStreetMap trực tiếp

Nếu bạn muốn tự import dữ liệu OSM mới:

### Bước 1: Download OSM data

```bash
# Tải Vietnam OSM data
wget https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
```

### Bước 2: Chạy script import

```bash
# Từ backend directory
python scripts/import_osm.py --file vietnam-latest.osm.pbf --area hanoi
```

Chi tiết tham số:
- `--file`: Đường dẫn đến file .osm.pbf
- `--area`: Khu vực muốn import (hanoi, hochiminhcity, danang, etc.)
- `--entity-types`: Loại entities (building, highway, amenity) - mặc định là tất cả

---

## Export database hiện tại

Nếu bạn muốn tạo backup hoặc chia sẻ database:

```bash
# Export từ container
docker exec citylens-postgres pg_dump -U citylens citylens_db > citylens_backup_$(date +%Y%m%d).sql

# Hoặc dùng script
./scripts/export_database.sh
```

---

## Troubleshooting

### Lỗi: "database does not exist"

```bash
# Tạo database
docker exec citylens-postgres psql -U citylens -c "CREATE DATABASE citylens_db;"
docker exec citylens-postgres psql -U citylens -d citylens_db -c "CREATE EXTENSION postgis;"
```

### Lỗi: "connection refused"

```bash
# Kiểm tra PostgreSQL đang chạy
docker ps | grep postgres

# Khởi động lại nếu cần
docker-compose up -d postgres
```

### Import quá lâu

File dump lớn có thể mất thời gian. Theo dõi progress:

```bash
# Xem logs PostgreSQL
docker-compose logs -f postgres

# Kiểm tra disk usage
docker exec citylens-postgres df -h
```

### Xóa dữ liệu và import lại

```bash
# Drop tất cả tables
docker exec citylens-postgres psql -U citylens -d citylens_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Import lại
docker exec -i citylens-postgres psql -U citylens -d citylens_db < citylens_dump.sql
```

---

## Thông tin Database

Sau khi import thành công, database sẽ có:

### Tables chính

- `osm_entities`: Tất cả entities từ OpenStreetMap
- `citizen_reports`: Báo cáo từ người dân
- `users`: Quản lý người dùng
- `spatial_ref_sys`: PostGIS spatial reference systems

### Extensions

- PostGIS: Xử lý dữ liệu địa lý
- pg_trgm: Full-text search
- uuid-ossp: Generate UUIDs

### Statistics

- Tổng entities: 487,000+
- Buildings: ~350,000
- Roads: ~80,000
- POIs: ~57,000
- Dung lượng: ~2-3GB

---

## Hỗ trợ

- GitHub Issues: https://github.com/PKA-Open-Dynamics/CityLens/issues
- Documentation: README.md

---

Copyright (c) 2025 CityLens Contributors
GNU General Public License v3.0
