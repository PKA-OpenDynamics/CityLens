# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(
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
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000", "*"]

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "citylens_secret"
    POSTGRES_DB: str = "citylens_db"
    POSTGRES_PORT: str = "5432"
    
    # GraphDB / Fuseki
    GRAPHDB_URL: str = "http://fuseki:3030"
    GRAPHDB_DATASET: str = "citylens"
    GRAPHDB_REPOSITORY: str = "citylens"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "citylens_realtime"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # External API Keys (Optional for data adapters)
    OPENWEATHER_API_KEY: Optional[str] = None
    TOMTOM_API_KEY: Optional[str] = None
    AQICN_API_KEY: Optional[str] = None  # WAQI API token from https://aqicn.org/api/
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
