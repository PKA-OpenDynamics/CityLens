# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Cấu hình ứng dụng CityLens Backend
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Cấu hình hệ thống"""
    
    # Thông tin ứng dụng
    PROJECT_NAME: str = "CityLens LOD Cloud"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = "Hệ thống thành phố thông minh sử dụng Linked Open Data"
    
    # Bảo mật
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 ngày
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # PostgreSQL + PostGIS
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "citylens"
    POSTGRES_PASSWORD: str = "citylens_password"
    POSTGRES_DB: str = "citylens_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "citylens_realtime"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # GraphDB / SPARQL Endpoint
    GRAPHDB_URL: str = "http://localhost:7200"
    GRAPHDB_REPOSITORY: str = "citylens"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "mp4", "mov"]
    
    # External APIs
    OPENWEATHER_API_KEY: Optional[str] = None
    OPENAQ_API_KEY: Optional[str] = None
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Gamification
    POINTS_PER_REPORT: int = 10
    POINTS_PER_VERIFICATION: int = 5
    REPUTATION_THRESHOLD_TRUSTED: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
