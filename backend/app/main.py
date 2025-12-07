# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## CityLens Smart City Platform API
    
    ### 🏙️ LOD-Based Architecture (3 Layers)
    
    **Layer 1: Geographic Foundation**
    - Administrative Boundaries (1 entity - Hanoi City)
    - Streets & Roads (253,611 entities)
    - Buildings (218,044 entities)
    - Points of Interest - POIs (15,341 entities)
    
    **Layer 2: Urban Infrastructure**
    - Sensor Data (Air Quality, Traffic)
    - Public Facilities
    
    **Layer 3: Citizen Data**
    - Reports & Issues
    - User Interactions
    
    ### 📊 Data Source
    All geographic data imported from **OpenStreetMap** with accurate coordinates for Hanoi area.
    
    ### 🔗 Standards Compliance
    - ETSI NGSI-LD for context data
    - GeoJSON for geographic features
    - RESTful API design
    
    ### 📍 Coverage Area
    - City: Hanoi, Vietnam
    - Bounding Box: (105.29°E, 20.56°N) to (106.02°E, 21.39°N)
    - Total Features: **486,997**
    
    ### 🚀 Quick Start
    1. Browse **Geographic Data** endpoints for streets, buildings, POIs
    2. Use **Reports** endpoints for citizen issue reporting
    3. Check **Statistics** for data overview
    
    ### 📚 Full Documentation
    - API Docs: `/docs` (this page)
    - ReDoc: `/redoc`
    - Geographic API Guide: See backend/GEOGRAPHIC_API_DOCS.md
    """,
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
        "docs": "/docs"
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
