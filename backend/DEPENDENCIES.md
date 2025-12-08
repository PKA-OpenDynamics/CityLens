# CityLens Backend - Dependencies

Tài liệu này liệt kê tất cả các thư viện và gói phần mềm được sử dụng trong dự án CityLens Backend.

## Phiên bản Python

- **Python**: 3.11+ (khuyến nghị 3.11 hoặc 3.12)

## Thư viện chính

### Core Framework

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [FastAPI](https://fastapi.tiangolo.com/) | 0.109.0 | MIT | Web framework hiện đại cho Python |
| [Uvicorn](https://www.uvicorn.org/) | 0.27.0 | BSD-3-Clause | ASGI server |
| [Pydantic](https://pydantic-docs.helpmanual.io/) | 2.6.0 | MIT | Data validation |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | 2.1.0 | MIT | Settings management |

### Database - PostgreSQL + PostGIS

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0.25 | MIT | SQL toolkit và ORM |
| [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/) | 0.14.3 | MIT | Spatial extension cho SQLAlchemy |
| [asyncpg](https://magicstack.github.io/asyncpg/) | 0.29.0 | Apache-2.0 | Async PostgreSQL driver |
| [psycopg2-binary](https://www.psycopg.org/) | 2.9.9 | LGPL | PostgreSQL adapter |
| [Alembic](https://alembic.sqlalchemy.org/) | 1.13.1 | MIT | Database migrations |

### Database - MongoDB

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [PyMongo](https://pymongo.readthedocs.io/) | 4.6.1 | Apache-2.0 | MongoDB driver |
| [Motor](https://motor.readthedocs.io/) | 3.3.2 | Apache-2.0 | Async MongoDB driver |

### Database - Redis

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [redis](https://redis-py.readthedocs.io/) | 5.0.1 | MIT | Redis client |

### Authentication & Security

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [python-jose](https://python-jose.readthedocs.io/) | 3.3.0 | MIT | JWT implementation |
| [passlib](https://passlib.readthedocs.io/) | 1.7.4 | BSD | Password hashing |
| [email-validator](https://github.com/JoshData/python-email-validator) | 2.1.0 | CC0-1.0 | Email validation |

### File Upload & Media

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [python-multipart](https://github.com/andrew-d/python-multipart) | 0.0.6 | Apache-2.0 | Multipart form data |
| [Pillow](https://pillow.readthedocs.io/) | 10.2.0 | HPND | Image processing |
| [cloudinary](https://cloudinary.com/documentation/python_integration) | 1.37.0 | MIT | Cloud media storage |

### HTTP Client

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [httpx](https://www.python-httpx.org/) | 0.26.0 | BSD-3-Clause | Async HTTP client |
| [requests](https://requests.readthedocs.io/) | 2.31.0 | Apache-2.0 | HTTP library |

### GIS & Geospatial

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Shapely](https://shapely.readthedocs.io/) | 2.0.2 | BSD-3-Clause | Geometric operations |
| [NumPy](https://numpy.org/) | 1.26.3 | BSD-3-Clause | Numerical computing |
| [osmium](https://osmcode.org/pyosmium/) | 3.7.0 | BSD-2-Clause | OSM data processing |

### Linked Open Data (Optional)

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [RDFLib](https://rdflib.readthedocs.io/) | 7.0.0 | BSD-3-Clause | RDF library |
| [SPARQLWrapper](https://sparqlwrapper.readthedocs.io/) | 2.0.0 | W3C | SPARQL endpoint access |

### System Monitoring

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [psutil](https://psutil.readthedocs.io/) | 5.9.8 | BSD-3-Clause | System utilities |

### Environment

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.0.0 | BSD-3-Clause | Environment variables |

## Dịch vụ bên ngoài (External Services)

Dự án sử dụng các API bên ngoài để thu thập dữ liệu thành phố thông minh:

| Dịch vụ | Mục đích | Giấy phép API |
|---------|----------|---------------|
| [OpenWeatherMap](https://openweathermap.org/) | Dữ liệu thời tiết | Free tier available |
| [AQICN](https://aqicn.org/) | Chỉ số chất lượng không khí | Free tier available |
| [TomTom](https://developer.tomtom.com/) | Dữ liệu giao thông | Free tier available |
| [OpenStreetMap](https://www.openstreetmap.org/) | Dữ liệu bản đồ | ODbL |

## Cài đặt

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt tất cả dependencies
pip install -r requirements.txt
```

## Tương thích giấy phép

Tất cả các thư viện được sử dụng đều có giấy phép tương thích với GPL-3.0:
- MIT License ✓
- BSD Licenses (2-Clause, 3-Clause) ✓
- Apache-2.0 ✓
- LGPL ✓

Dự án CityLens Backend được phát hành theo giấy phép **GNU General Public License v3.0 (GPL-3.0)**.
