# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

import json
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra='ignore'  # Ignore extra fields from .env
    )
    
    PROJECT_NAME: str = "CityLens"
    VERSION: str = "0.3.0"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "secret-key-change-in-production-citylens-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8081", "*"]
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Allow comma-separated string or JSON array for CORS origins"""
        if v is None or v == "":
            return []
        if isinstance(v, str):
            # If user provides JSON array string, try to parse
            if v.strip().startswith('['):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Fallback: comma-separated list
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Database (PostgreSQL with PostGIS)
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "citylens_secret"
    POSTGRES_DB: str = "citylens_db"
    POSTGRES_PORT: str = "5432"
    
    # GraphDB / Fuseki
    GRAPHDB_URL: str = "http://fuseki:3030"
    GRAPHDB_DATASET: str = "citylens"
    GRAPHDB_REPOSITORY: str = "citylens"
    
    # MongoDB (Docker - for Web Dashboard)
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "citylens_realtime"
    
    # MongoDB Atlas (Cloud - for Mobile App)
    MONGODB_ATLAS_URI: Optional[str] = None
    MONGODB_ATLAS_DB: str = "citylens_app"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External API Keys (Optional for data adapters)
    OPENWEATHER_API_KEY: Optional[str] = None
    TOMTOM_API_KEY: Optional[str] = None
    AQICN_API_KEY: Optional[str] = None  # WAQI API token from https://aqicn.org/api/
    GEMINI_API_KEY: Optional[str] = None  # Google Gemini API key for AI chat
    
    @property
    def REDIS_URL(self) -> str:
        """Redis URL for cache connections"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Async database URI for AsyncSession"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Alias for SQLALCHEMY_DATABASE_URI"""
        return self.SQLALCHEMY_DATABASE_URI
    
    @property
    def SQLALCHEMY_SYNC_DATABASE_URI(self) -> str:
        """Sync database URI for legacy Session"""
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
