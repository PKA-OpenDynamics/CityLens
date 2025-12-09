# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.mongodb import mongodb
from app.db.mongodb_atlas import mongodb_atlas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events"""
    # Startup: Connect to MongoDB (Docker - for Web Dashboard)
    await mongodb.connect_db()
    
    # Startup: Connect to MongoDB Atlas (Cloud - for Mobile App)
    await mongodb_atlas.connect()
    
    yield
    
    # Shutdown: Close MongoDB connections
    await mongodb.close_db()
    await mongodb_atlas.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CityLens Smart City Platform - REST API for urban data management with FiWARE NGSI-LD",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "CityLens Team",
        "email": "contact@citylens.vn",
    },
    license_info={
        "name": "GNU General Public License v3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html",
    },
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def root():
    return {
        "message": "Welcome to CityLens NGSI-LD Context Broker",
        "version": settings.VERSION,
        "docs": "/docs",
        "features": [
            "FiWARE NGSI-LD Smart Data Models",
            "Web Dashboard Authentication & Authorization (MongoDB Docker)",
            "Mobile App Authentication & Reports (MongoDB Atlas)",
            "Real-time Urban Data Management"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "citylens-backend",
        "version": settings.VERSION
    }

# Use the new API v1 router with all endpoints
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

