# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
NGSI-LD API Endpoints
Standard: ETSI GS CIM 009 V1.6.1

Implements:
- Entity CRUD operations
- Query entities with filters
- Geo-queries
- Temporal queries (future)
- Subscriptions (future)
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.api.deps import get_db
from app.schemas.ngsi_ld.base import NGSILDEntity, NGSILDEntityFragment
from app.schemas.ngsi_ld.query import NGSILDQuery
from app.services.lod.ngsi_ld_service import ngsi_ld_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ngsi-ld/v1", tags=["NGSI-LD"])


# ============================================================
# ENTITY CRUD OPERATIONS
# ============================================================

@router.post(
    "/entities",
    status_code=201,
    summary="Create Entity",
    description="Create a new NGSI-LD entity"
)
async def create_entity(
    entity: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Create NGSI-LD Entity
    
    **Standard:** ETSI GS CIM 009 V1.6.1 Section 5.6.1
    
    **Request Body:**
    ```json
    {
      "id": "urn:ngsi-ld:AirQualityObserved:HCM-D1-001",
      "type": "AirQualityObserved",
      "dateObserved": {
        "type": "Property",
        "value": "2025-11-25T10:00:00Z"
      },
      "location": {
        "type": "GeoProperty",
        "value": {
          "type": "Point",
          "coordinates": [106.6927, 10.7769]
        }
      },
      "@context": [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
      ]
    }
    ```
    
    **Success Response:**
    - Status: 201 Created
    - Headers: Location: /ngsi-ld/v1/entities/{entityId}
    
    **Error Responses:**
    - 400: Bad Request (invalid entity structure)
    - 409: Conflict (entity already exists)
    """
    try:
        # Validate entity structure
        entity_id = entity.get("id")
        entity_type = entity.get("type")
        
        if not entity_id or not entity_type:
            raise HTTPException(
                status_code=400,
                detail="Entity must have 'id' and 'type' fields"
            )
        
        if not entity_id.startswith("urn:ngsi-ld:"):
            raise HTTPException(
                status_code=400,
                detail="Entity ID must be a valid URI starting with 'urn:ngsi-ld:'"
            )
        
        # Check if entity already exists
        existing = await ngsi_ld_service.get_entity_by_id(entity_id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Entity {entity_id} already exists"
            )
        
        # Convert dict to NGSILDEntity for validation
        # (For now, accept dict directly to be flexible)
        
        # Create entity in all stores
        result = await ngsi_ld_service.create_entity(
            entity=entity,  # type: ignore
            db=db,
            store_in_postgres=True,
            store_in_graphdb=True,
            convert_to_sosa=True
        )
        
        return JSONResponse(
            status_code=201,
            content=result,
            headers={
                "Location": f"/ngsi-ld/v1/entities/{entity_id}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/entities/{entity_id}",
    summary="Retrieve Entity",
    description="Retrieve an NGSI-LD entity by ID"
)
async def get_entity(
    entity_id: str = Path(..., description="Entity ID (URI)"),
    attrs: Optional[str] = Query(
        None,
        description="Comma-separated list of attributes to include"
    ),
    options: Optional[str] = Query(
        None,
        description="Options: keyValues, sysAttrs"
    )
):
    """
    Retrieve NGSI-LD Entity by ID
    
    **Standard:** ETSI GS CIM 009 V1.6.1 Section 5.6.2
    
    **Path Parameters:**
    - `entity_id`: Entity URI (e.g., urn:ngsi-ld:AirQualityObserved:HCM-D1-001)
    
    **Query Parameters:**
    - `attrs`: Filter attributes (e.g., "location,dateObserved")
    - `options`: Response format options
      - `keyValues`: Simplified format without type/metadata
      - `sysAttrs`: Include system attributes (createdAt, modifiedAt)
    
    **Success Response:**
    - Status: 200 OK
    - Body: Entity in NGSI-LD format
    
    **Error Responses:**
    - 404: Entity not found
    """
    try:
        entity = await ngsi_ld_service.get_entity_by_id(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity {entity_id} not found"
            )
        
        # Filter attributes if requested
        if attrs:
            attr_list = [a.strip() for a in attrs.split(",")]
            entity = {k: v for k, v in entity.items() if k in ["id", "type"] + attr_list}
        
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/entities",
    summary="Query Entities",
    description="Query NGSI-LD entities with filters"
)
async def query_entities(
    # Entity Type
    type: Optional[str] = Query(
        None,
        description="Entity type filter (comma-separated for multiple)"
    ),
    # ID Pattern
    id: Optional[str] = Query(None, description="Entity ID"),
    idPattern: Optional[str] = Query(None, description="ID regex pattern"),
    
    # Attributes
    attrs: Optional[str] = Query(
        None,
        description="Attributes to include"
    ),
    
    # Query Language
    q: Optional[str] = Query(
        None,
        description="Query filter (e.g., 'temperature>25;status==active')"
    ),
    
    # Geo-Query
    georel: Optional[str] = Query(
        None,
        description="Geo relationship (e.g., 'near;maxDistance==5000')"
    ),
    geometry: Optional[str] = Query(
        None,
        description="Geometry type: Point, Polygon, LineString"
    ),
    coordinates: Optional[str] = Query(
        None,
        description="Coordinates (format depends on geometry)"
    ),
    geoproperty: str = Query(
        "location",
        description="GeoProperty to query against"
    ),
    
    # Pagination
    limit: int = Query(20, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    
    # Options
    options: Optional[str] = Query(None, description="Query options"),
    
    db: Session = Depends(get_db)
):
    """
    Query NGSI-LD Entities
    
    **Standard:** ETSI GS CIM 009 V1.6.1 Section 5.7.2
    
    **Query Examples:**
    
    1. **Get all entities of a type:**
    ```
    GET /ngsi-ld/v1/entities?type=AirQualityObserved
    ```
    
    2. **Geo-query - find entities near a point:**
    ```
    GET /ngsi-ld/v1/entities?type=CitizenReport&georel=near;maxDistance==1000&geometry=Point&coordinates=[106.6927,10.7769]
    ```
    
    3. **Property query:**
    ```
    GET /ngsi-ld/v1/entities?type=AirQualityObserved&q=airQualityIndex>100
    ```
    
    4. **Combined query:**
    ```
    GET /ngsi-ld/v1/entities?type=CitizenReport&q=status==pending;priority==high&limit=50
    ```
    
    **Success Response:**
    - Status: 200 OK
    - Body: Array of entities
    
    **Headers:**
    - Link: Pagination links (if applicable)
    - Count: Total number of matching entities (optional)
    """
    try:
        # Build query object
        query_params = NGSILDQuery(
            type=type,
            id=id,
            idPattern=idPattern,
            attrs=attrs,
            q=q,
            georel=georel,
            geometry=geometry,  # type: ignore
            coordinates=coordinates,
            geoproperty=geoproperty,
            limit=limit,
            offset=offset,
            options=options
        )
        
        # Execute query
        entities = await ngsi_ld_service.query_entities(query_params, db)
        
        # Build response
        response = {
            "entities": entities,
            "count": len(entities)
        }
        
        # Add pagination links if needed
        if len(entities) == limit:
            response["next"] = f"/ngsi-ld/v1/entities?{query_params}&offset={offset + limit}"
        
        return entities  # Return array directly per NGSI-LD spec
        
    except Exception as e:
        logger.error(f"Error querying entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/entities/{entity_id}/attrs",
    status_code=204,
    summary="Update Entity Attributes",
    description="Partially update entity attributes"
)
async def update_entity_attributes(
    entity_id: str = Path(..., description="Entity ID"),
    attributes: Dict[str, Any] = Body(..., description="Attributes to update"),
    db: Session = Depends(get_db)
):
    """
    Update Entity Attributes (Partial Update)
    
    **Standard:** ETSI GS CIM 009 V1.6.1 Section 5.6.3
    
    **Request Body:**
    ```json
    {
      "status": {
        "type": "Property",
        "value": "resolved"
      },
      "resolvedAt": {
        "type": "Property",
        "value": "2025-11-25T15:30:00Z"
      }
    }
    ```
    
    **Success Response:**
    - Status: 204 No Content
    
    **Error Responses:**
    - 404: Entity not found
    - 400: Invalid attribute structure
    """
    try:
        # Check if entity exists
        existing = await ngsi_ld_service.get_entity_by_id(entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Update attributes
        success = await ngsi_ld_service.update_entity(entity_id, attributes, db)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update entity")
        
        return JSONResponse(status_code=204, content=None)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/entities/{entity_id}",
    status_code=204,
    summary="Delete Entity",
    description="Delete an NGSI-LD entity"
)
async def delete_entity(
    entity_id: str = Path(..., description="Entity ID"),
    db: Session = Depends(get_db)
):
    """
    Delete NGSI-LD Entity
    
    **Standard:** ETSI GS CIM 009 V1.6.1 Section 5.6.5
    
    **Success Response:**
    - Status: 204 No Content
    
    **Error Responses:**
    - 404: Entity not found
    """
    try:
        # Check if entity exists
        existing = await ngsi_ld_service.get_entity_by_id(entity_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Delete entity
        success = await ngsi_ld_service.delete_entity(entity_id, db)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete entity")
        
        return JSONResponse(status_code=204, content=None)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ADDITIONAL ENDPOINTS
# ============================================================

@router.get(
    "/types",
    summary="Get Entity Types",
    description="Retrieve list of entity types in the system"
)
async def get_entity_types():
    """
    Get list of available entity types
    
    **Response:**
    ```json
    {
      "types": [
        "AirQualityObserved",
        "WeatherObserved",
        "TrafficFlowObserved",
        "CitizenReport",
        ...
      ]
    }
    ```
    """
    return {
        "types": [
            "AirQualityObserved",
            "WeatherObserved",
            "TrafficFlowObserved",
            "RoadAccident",
            "OffStreetParking",
            "ParkingSpot",
            "Streetlight",
            "WaterQualityObserved",
            "CitizenReport"
        ]
    }


@router.get(
    "/@context",
    summary="Get JSON-LD Context",
    description="Retrieve the JSON-LD context for CityLens"
)
async def get_context():
    """
    Get JSON-LD Context
    
    Returns the @context used by CityLens entities.
    """
    return {
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "http://citylens.io/context/citylens-context.jsonld"
        ]
    }


# ============================================================
# BATCH OPERATIONS (Future)
# ============================================================

@router.post(
    "/entityOperations/create",
    status_code=201,
    summary="Batch Create Entities",
    description="Create multiple entities in a single operation"
)
async def batch_create_entities(
    entities: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Batch Create Entities
    
    **Request Body:**
    ```json
    {
      "entities": [
        { "id": "...", "type": "...", ... },
        { "id": "...", "type": "...", ... }
      ]
    }
    ```
    
    **Response:**
    ```json
    {
      "success": ["entity_id1", "entity_id2"],
      "errors": []
    }
    ```
    """
    success = []
    errors = []
    
    for entity in entities:
        try:
            result = await ngsi_ld_service.create_entity(entity, db)  # type: ignore
            success.append(result["id"])
        except Exception as e:
            errors.append({
                "entityId": entity.get("id"),
                "error": str(e)
            })
    
    return {
        "success": success,
        "errors": errors
    }

