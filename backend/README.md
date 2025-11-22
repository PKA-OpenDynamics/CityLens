# CityLens Backend

Backend API cho hệ thống thành phố thông minh CityLens sử dụng Linked Open Data.

## Công nghệ

- **Framework**: FastAPI 0.109
- **Database**: PostgreSQL 15 + PostGIS 3.4
- **Document Store**: MongoDB 7.0
- **Cache**: Redis 7.2
- **Graph Database**: Apache Jena Fuseki / Blazegraph
- **Task Queue**: Celery + Redis
- **API Standards**: REST, NGSI-LD, SPARQL

## Cài đặt

### Yêu cầu hệ thống

- Python 3.11+
- PostgreSQL 15+ với PostGIS
- MongoDB 7.0+
- Redis 7.0+

### Cài đặt từ mã nguồn

```bash
# Clone repository
git clone https://github.com/your-org/citylens.git
cd citylens/backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Copy file cấu hình
cp .env.example .env
# Chỉnh sửa .env với thông tin của bạn

# Chạy migrations
alembic upgrade head

# Chạy server
uvicorn app.main:app --reload
```

## Chạy với Docker

```bash
docker build -t citylens-backend .
docker run -p 8000:8000 citylens-backend
```

## API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Cấu hình & security
│   ├── db/           # Database connections
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── tasks/        # Celery tasks
│   └── utils/        # Utilities
├── tests/            # Test cases
└── requirements.txt  # Dependencies
```

## License

MIT License - xem file [LICENSE](../LICENSE)
