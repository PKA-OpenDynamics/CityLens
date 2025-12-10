# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Environment Detection Utility
Automatically detect if running in local development or production (Cloudflare).
"""

from enum import Enum
from typing import Optional
import os
import socket


class Environment(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"
    STAGING = "staging"
    DOCKER = "docker"


class EnvironmentDetector:
    """Detect the current running environment."""
    
    _instance: Optional['EnvironmentDetector'] = None
    _environment: Optional[Environment] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def detect(cls, request_headers: dict = None) -> Environment:
        """
        Detect environment based on various signals.
        
        Priority:
        1. Explicit ENV variable
        2. Cloudflare headers (production)
        3. Docker environment
        4. Hostname check
        """
        # Check if already cached
        if cls._environment:
            return cls._environment
        
        # 1. Check explicit environment variable
        env_var = os.getenv("CITYLENS_ENV", os.getenv("ENVIRONMENT", ""))
        if env_var:
            env_lower = env_var.lower()
            if env_lower == "production" or env_lower == "prod":
                cls._environment = Environment.PRODUCTION
                return cls._environment
            elif env_lower == "staging":
                cls._environment = Environment.STAGING
                return cls._environment
            elif env_lower == "local" or env_lower == "development":
                cls._environment = Environment.LOCAL
                return cls._environment
        
        # 2. Check for Cloudflare headers (means we're behind Cloudflare = production)
        if request_headers:
            cf_headers = [
                "CF-Connecting-IP",
                "CF-Ray",
                "CF-IPCountry",
                "X-Forwarded-For"  # Common in production load balancers
            ]
            for header in cf_headers:
                if header in request_headers or header.lower() in request_headers:
                    cls._environment = Environment.PRODUCTION
                    return cls._environment
        
        # 3. Check for Docker environment
        if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
            # In Docker but could be local docker-compose or production
            # Check for production indicators
            if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RENDER_EXTERNAL_URL"):
                cls._environment = Environment.PRODUCTION
            elif os.getenv("NETLIFY"):
                cls._environment = Environment.PRODUCTION
            else:
                cls._environment = Environment.DOCKER
            return cls._environment
        
        # 4. Check hostname
        try:
            hostname = socket.gethostname().lower()
            if any(prod_indicator in hostname for prod_indicator in 
                   ["prod", "production", "live", "citylens"]):
                cls._environment = Environment.PRODUCTION
                return cls._environment
        except:
            pass
        
        # 5. Check if running on typical local ports
        # If we get here, assume local development
        cls._environment = Environment.LOCAL
        return cls._environment
    
    @classmethod
    def is_local(cls) -> bool:
        """Check if running in local development."""
        return cls.detect() in (Environment.LOCAL, Environment.DOCKER)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production."""
        return cls.detect() == Environment.PRODUCTION
    
    @classmethod
    def reset(cls):
        """Reset cached environment (useful for testing)."""
        cls._environment = None


def get_environment() -> Environment:
    """Get the current environment."""
    return EnvironmentDetector.detect()


def is_local() -> bool:
    """Check if running locally."""
    return EnvironmentDetector.is_local()


def is_production() -> bool:
    """Check if running in production."""
    return EnvironmentDetector.is_production()


# URL Configuration based on environment
class URLConfig:
    """Dynamic URL configuration based on environment."""
    
    # Local development URLs
    LOCAL_URLS = {
        "backend": "http://localhost:8000",
        "frontend": "http://localhost:3000",
        "fuseki": "http://localhost:7200",
        "mongodb": "mongodb://localhost:27017",
    }
    
    # Docker (local docker-compose) URLs
    DOCKER_URLS = {
        "backend": "http://backend:8000",
        "frontend": "http://localhost:3000",
        "fuseki": "http://fuseki:3030",
        "mongodb": "mongodb://mongodb:27017",
    }
    
    # Production URLs (Cloudflare, etc.)
    PRODUCTION_URLS = {
        "backend": os.getenv("BACKEND_URL", "https://api.citylens.vn"),
        "frontend": os.getenv("FRONTEND_URL", "https://citylens.vn"),
        "fuseki": os.getenv("FUSEKI_URL", "https://fuseki.citylens.vn"),
        "mongodb": os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
    }
    
    @classmethod
    def get_urls(cls) -> dict:
        """Get URLs for current environment."""
        env = get_environment()
        
        if env == Environment.LOCAL:
            return cls.LOCAL_URLS.copy()
        elif env == Environment.DOCKER:
            return cls.DOCKER_URLS.copy()
        else:
            return cls.PRODUCTION_URLS.copy()
    
    @classmethod
    def get_backend_url(cls) -> str:
        """Get backend API URL."""
        return cls.get_urls()["backend"]
    
    @classmethod
    def get_frontend_url(cls) -> str:
        """Get frontend URL."""
        return cls.get_urls()["frontend"]
    
    @classmethod
    def get_fuseki_url(cls) -> str:
        """Get Fuseki/GraphDB URL."""
        return cls.get_urls()["fuseki"]
    
    @classmethod
    def get_allowed_origins(cls) -> list:
        """Get CORS allowed origins for current environment."""
        env = get_environment()
        
        if env in (Environment.LOCAL, Environment.DOCKER):
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8081",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ]
        else:
            # Production: allow Cloudflare tunnels and official domains
            return [
                "https://citylens.vn",
                "https://*.citylens.vn",
                "https://*.netlify.app",
                "https://*.trycloudflare.com",
                os.getenv("FRONTEND_URL", "https://citylens.vn"),
            ]
