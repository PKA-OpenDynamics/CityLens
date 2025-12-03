from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ngsi_ld import Entity
from app.repositories.entity_repository import EntityRepository

router = APIRouter()

@router.post("/", response_model=Entity, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity: Entity,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new NGSI-LD Entity.
    """
    repo = EntityRepository(db)
    try:
        db_entity = await repo.create_entity(entity)
        # Return the JSON data stored
        return db_entity.data
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/{entity_id}", response_model=Entity)
async def get_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve an Entity by ID.
    """
    repo = EntityRepository(db)
    db_entity = await repo.get_entity(entity_id)
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity.data

@router.get("/", response_model=List[Entity])
async def query_entities(
    type: Optional[str] = Query(None, description="Filter by Entity Type"),
    lat: Optional[float] = Query(None, description="Latitude for geo-query"),
    lon: Optional[float] = Query(None, description="Longitude for geo-query"),
    radius: Optional[float] = Query(None, description="Radius in meters (requires lat/lon)"),
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Query Entities. Supports:
    - Filtering by Type
    - Geo-spatial search (near point)
    - Pagination
    """
    repo = EntityRepository(db)
    
    if lat is not None and lon is not None and radius is not None:
        # Geo Query
        entities = await repo.get_entities_near(lat, lon, radius, type)
    else:
        # Standard List
        entities = await repo.list_entities(type, limit, offset)
        
    # Extract JSON data from DB models
    return [e.data for e in entities]

