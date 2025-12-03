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
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000", "*"]

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "citylens_secret"
    POSTGRES_DB: str = "citylens_db"
    POSTGRES_PORT: str = "5432"
    
    # External API Keys (Optional for data adapters)
    OPENWEATHER_API_KEY: Optional[str] = None
    TOMTOM_API_KEY: Optional[str] = None
    AQICN_API_KEY: Optional[str] = None  # WAQI API token from https://aqicn.org/api/
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
