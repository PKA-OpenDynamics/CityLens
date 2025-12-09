# Hướng dẫn Đóng góp cho CityLens Backend

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án CityLens Backend! Tài liệu này cung cấp hướng dẫn để đóng góp vào backend API.

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

- Python 3.11+
- PostgreSQL 15+ với PostGIS
- Redis 7+ (optional)
- MongoDB 7+ (optional)

### Cài đặt

```bash
# Clone repository
git clone https://github.com/PKA-Open-Dynamics/CityLens.git
cd CityLens/backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Copy và cấu hình environment
cp .env.example .env
# Chỉnh sửa .env với thông tin database của bạn

# Chạy migrations
alembic upgrade head

# Chạy server
uvicorn app.main:app --reload
```

## Cấu trúc dự án

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   └── endpoints/   # Route handlers
│   ├── adapters/        # External service adapters
│   ├── core/            # Configuration & security
│   ├── db/              # Database connections
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # Application entry
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
├── graphdb/             # LOD ontology & context
└── requirements.txt     # Dependencies
```

## Chuẩn code

### Python Style

- **PEP 8**: Tuân thủ PEP 8 style guide
- **Black**: Sử dụng Black formatter (line length 100)
- **Type hints**: Sử dụng type annotations
- **Docstrings**: Google-style docstrings

### License Header

Mỗi file Python phải có license header:

```python
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)
```

### API Conventions

- RESTful endpoints với prefix `/api/v1/`
- NGSI-LD endpoints với prefix `/ngsi-ld/v1/`
- Sử dụng Pydantic schemas cho validation
- HTTP status codes chuẩn

### Database

- Migrations với Alembic
- Models kế thừa từ `Base`
- PostGIS geometries với GeoAlchemy2

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

## Testing

```bash
# Chạy tests
pytest

# Với coverage
pytest --cov=app
```

## Liên hệ

- Issues: [GitHub Issues](https://github.com/PKA-Open-Dynamics/CityLens/issues)
- Email: citylens@example.com
