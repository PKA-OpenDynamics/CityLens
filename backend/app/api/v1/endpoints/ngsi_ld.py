# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
NGSI-LD Context Broker API
ETSI GS CIM 009 V1.8.1 compliant

Full CRUD operations for NGSI-LD entities:
- POST /ngsi-ld/v1/entities - Create entity
- GET /ngsi-ld/v1/entities - Query entities
- GET /ngsi-ld/v1/entities/{id} - Retrieve entity
- PATCH /ngsi-ld/v1/entities/{id}/attrs - Update entity attributes
- DELETE /ngsi-ld/v1/entities/{id} - Delete entity
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from geoalchemy2.functions import ST_Distance, ST_GeomFromText, ST_AsGeoJSON
import json
from datetime import datetime

from app.core.database import get_db
from app.models.db_models import EntityDB
from app.schemas.fiware import (
    WeatherObserved, WeatherObservedCreate,
    AirQualityObserved, AirQualityObservedCreate,
    TrafficFlowObserved, TrafficFlowObservedCreate,
    ParkingSpot, ParkingSpotCreate,
    CivicIssueTracking, CivicIssueTrackingCreate
)
from app.schemas.fiware.weather import to_ngsi_ld_entity as weather_to_ngsi_ld
from app.schemas.fiware.air_quality import to_ngsi_ld_entity as aqi_to_ngsi_ld
from app.schemas.fiware.traffic import to_ngsi_ld_entity as traffic_to_ngsi_ld
from app.schemas.fiware.parking import to_ngsi_ld_entity as parking_to_ngsi_ld
from app.schemas.fiware.civic_issue import to_ngsi_ld_entity as civic_to_ngsi_ld

router = APIRouter(prefix="/ngsi-ld/v1", tags=["NGSI-LD Context Broker"])


def extract_geometry_from_entity(entity_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract geometry from NGSI-LD entity for PostGIS storage.
    Returns WKT string.
    """
    if "location" not in entity_data:
        return None
    
    location = entity_data["location"]
    if location.get("type") != "GeoProperty":
        return None
    
    geojson = location.get("value", {})
    geom_type = geojson.get("type")
    coords = geojson.get("coordinates")
    
    if not geom_type or not coords:
        return None
    
    # Convert GeoJSON to WKT
    if geom_type == "Point":
        return f"SRID=4326;POINT({coords[0]} {coords[1]})"
    elif geom_type == "LineString":
        points = ", ".join([f"{c[0]} {c[1]}" for c in coords])
        return f"SRID=4326;LINESTRING({points})"
    elif geom_type == "Polygon":
        rings = []
        for ring in coords:
            points = ", ".join([f"{c[0]} {c[1]}" for c in ring])
            rings.append(f"({points})")
        return f"SRID=4326;POLYGON({', '.join(rings)})"
    
    return None


@router.post("/entities", status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new NGSI-LD entity.
    
    Supports FiWARE Smart Data Models:
    - WeatherObserved
    - AirQualityObserved
    - TrafficFlowObserved
    - ParkingSpot
    - CivicIssueTracking
    """
    # Validate required fields
    if "id" not in entity or "type" not in entity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity must have 'id' and 'type' fields"
        )
    
    entity_id = entity["id"]
    entity_type = entity["type"]
    
    # Check if entity already exists
    result = await db.execute(
        select(EntityDB).where(EntityDB.id == entity_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entity {entity_id} already exists"
        )
    
    # Extract geometry for spatial indexing
    geometry_wkt = extract_geometry_from_entity(entity)
    
    # Create entity
    db_entity = EntityDB(
        id=entity_id,
        type=entity_type,
        data=entity,
        location_geom=geometry_wkt,
        created_at=datetime.utcnow()
    )
    
    db.add(db_entity)
    await db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=entity,
        headers={"Location": f"/ngsi-ld/v1/entities/{entity_id}"}
    )


@router.get("/entities")
async def query_entities(
    type: Optional[str] = Query(None, description="Entity type filter"),
    q: Optional[str] = Query(None, description="Query filter (NGSI-LD query language)"),
    georel: Optional[str] = Query(None, description="Geo-relationship: near, within, etc."),
    geometry: Optional[str] = Query(None, description="Geometry type: Point, Polygon"),
    coordinates: Optional[str] = Query(None, description="Coordinates as JSON array"),
    geoproperty: Optional[str] = Query("location", description="Geo-property name"),
    limit: int = Query(20, ge=1, le=1000, description="Result limit"),
    offset: int = Query(0, ge=0, description="Result offset"),
    db: AsyncSession = Depends(get_db)
):
    """
    Query NGSI-LD entities with filtering.
    
    Supports:
    - Type filtering
    - Geo-spatial queries (near, within)
    - Pagination
    """
    query = select(EntityDB)
    
    # Type filter
    if type:
        query = query.where(EntityDB.type == type)
    
    # Geo-spatial query
    if georel and coordinates:
        try:
            coords = json.loads(coordinates)
            
            if georel.startswith("near"):
                # Extract distance from georel (e.g., "near;maxDistance==5000")
                max_distance = 5000  # default 5km
                if "maxDistance" in georel:
                    parts = georel.split("==")
                    if len(parts) == 2:
                        max_distance = float(parts[1])
                
                # Create point for distance query
                point_wkt = f"SRID=4326;POINT({coords[0]} {coords[1]})"
                query = query.where(
                    ST_Distance(
                        EntityDB.location_geom,
                        ST_GeomFromText(point_wkt)
                    ) <= max_distance
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid geo-query: {str(e)}"
            )
    
    # Pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    entities = result.scalars().all()
    
    # Return NGSI-LD entities
    return [entity.to_ngsi_ld() for entity in entities]


@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific NGSI-LD entity by ID.
    """
    result = await db.execute(
        select(EntityDB).where(EntityDB.id == entity_id)
    )
    entity = result.scalar_one_or_none()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found"
        )
    
    return entity.to_ngsi_ld()


@router.patch("/entities/{entity_id}/attrs")
async def update_entity_attributes(
    entity_id: str,
    attributes: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Update entity attributes (partial update).
    """
    result = await db.execute(
        select(EntityDB).where(EntityDB.id == entity_id)
    )
    entity = result.scalar_one_or_none()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found"
        )
    
    # Update attributes in JSONB data
    entity_data = entity.data.copy()
    entity_data.update(attributes)
    
    # Update geometry if location changed
    if "location" in attributes:
        geometry_wkt = extract_geometry_from_entity(entity_data)
        entity.location_geom = geometry_wkt
    
    entity.data = entity_data
    entity.modified_at = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "updated"}


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an NGSI-LD entity.
    """
    result = await db.execute(
        delete(EntityDB).where(EntityDB.id == entity_id)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found"
        )
    
    await db.commit()
    return None


@router.get("/types")
async def get_entity_types(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of entity types available in the system.
    """
    result = await db.execute(
        select(EntityDB.type).distinct()
    )
    types = result.scalars().all()
    
    return {
        "types": [
            {"type": t, "count": None}  # Could add count if needed
            for t in types
        ]
    }


# Helper endpoints for FiWARE Smart Data Models

@router.post("/entities/weather", status_code=status.HTTP_201_CREATED)
async def create_weather_entity(
    data: WeatherObservedCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create WeatherObserved entity using FiWARE Smart Data Model.
    """
    entity_id = f"urn:ngsi-ld:WeatherObserved:Hanoi:{int(data.dateObserved.timestamp())}"
    entity = weather_to_ngsi_ld(data, entity_id)
    
    return await create_entity(entity, db)


@router.post("/entities/air-quality", status_code=status.HTTP_201_CREATED)
async def create_air_quality_entity(
    data: AirQualityObservedCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create AirQualityObserved entity using FiWARE Smart Data Model.
    """
    entity_id = f"urn:ngsi-ld:AirQualityObserved:Hanoi:{int(data.dateObserved.timestamp())}"
    entity = aqi_to_ngsi_ld(data, entity_id)
    
    return await create_entity(entity, db)


@router.post("/entities/traffic", status_code=status.HTTP_201_CREATED)
async def create_traffic_entity(
    data: TrafficFlowObservedCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create TrafficFlowObserved entity using FiWARE Smart Data Model.
    """
    entity_id = f"urn:ngsi-ld:TrafficFlowObserved:Hanoi:{int(data.dateObserved.timestamp())}"
    entity = traffic_to_ngsi_ld(data, entity_id)
    
    return await create_entity(entity, db)


@router.post("/entities/civic-issue", status_code=status.HTTP_201_CREATED)
async def create_civic_issue_entity(
    data: CivicIssueTrackingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create CivicIssueTracking entity using FiWARE Smart Data Model.
    """
    entity_id = f"urn:ngsi-ld:CivicIssueTracking:Hanoi:{int(data.dateCreated.timestamp())}"
    entity = civic_to_ngsi_ld(data, entity_id)
    
    return await create_entity(entity, db)
