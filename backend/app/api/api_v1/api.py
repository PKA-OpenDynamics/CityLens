from fastapi import APIRouter
from app.api.api_v1.endpoints import entities, hanoi_data, osm_management, stats, osm_query

api_router = APIRouter()
api_router.include_router(entities.router, prefix="/ngsi-ld/v1/entities", tags=["NGSI-LD Entities"])
api_router.include_router(stats.router, prefix="/api/v1", tags=["Statistics & Monitoring"])
api_router.include_router(hanoi_data.router, prefix="/api/v1/hanoi-data", tags=["Hanoi Data Ingestion"])
api_router.include_router(osm_management.router, prefix="/api/v1/osm-management", tags=["OSM Data Management"])
api_router.include_router(osm_query.router, prefix="/api/v1/osm", tags=["OSM Data Query"])

