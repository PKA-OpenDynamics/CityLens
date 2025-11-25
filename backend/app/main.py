# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
FastAPI main application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1 import ngsi_ld_router  # NGSI-LD router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION + "\n\n**Standards:** NGSI-LD | SOSA/SSN | FiWARE Smart Data Models",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# NGSI-LD API (mounted at root level per ETSI standard)
# Available at: /ngsi-ld/v1/...
app.include_router(ngsi_ld_router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CityLens LOD Cloud API",
        "version": settings.VERSION,
        "description": "Smart City Platform using Linked Open Data",
        "standards": {
            "ngsi_ld": "ETSI GS CIM 009 V1.6.1",
            "sosa_ssn": "W3C SOSA/SSN Ontology",
            "fiware": "FiWARE Smart Data Models"
        },
        "endpoints": {
            "api_docs": f"{settings.API_V1_STR}/docs",
            "ngsi_ld": "/ngsi-ld/v1/entities",
            "sparql": "http://localhost:7200/citylens/sparql (GraphDB)"
        },
        "data_layers": {
            "layer_1": "Geographic Foundation (OSM)",
            "layer_2": "Urban Infrastructure (Sensors)",
            "layer_3": "Citizen Data (Reports)"
        }
    }


@app.get("/health")
async def health_check():
    """Kiểm tra sức khỏe hệ thống"""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
