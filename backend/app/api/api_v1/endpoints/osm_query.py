"""
API endpoints for querying OSM Administrative Areas and Facilities from PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from geoalchemy2.functions import ST_AsGeoJSON, ST_Distance, ST_DWithin
from geoalchemy2.shape import to_shape
import json

from app.core.database import get_db
from app.models.osm_models import AdministrativeArea, Facility

router = APIRouter()


@router.get("/admin-areas", response_model=Dict[str, Any])
async def get_administrative_areas(
    admin_level: Optional[int] = Query(None, description="Filter by admin level (4=City, 6=District, 8=Ward)"),
    parent_id: Optional[int] = Query(None, description="Filter by parent area ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get administrative areas with optional filtering.
    
    Query parameters:
    - admin_level: 4 (City), 6 (District), 8 (Ward)
    - parent_id: Get children of specific area
    - search: Search in name fields
    - limit/offset: Pagination
    """
    query = select(AdministrativeArea)
    
    if admin_level:
        query = query.where(AdministrativeArea.admin_level == admin_level)
    
    if parent_id:
        query = query.where(AdministrativeArea.parent_id == parent_id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (AdministrativeArea.name.ilike(search_pattern)) |
            (AdministrativeArea.name_vi.ilike(search_pattern)) |
            (AdministrativeArea.name_en.ilike(search_pattern))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get paginated results
    query = query.limit(limit).offset(offset).order_by(AdministrativeArea.admin_level, AdministrativeArea.name)
    result = await db.execute(query)
    areas = result.scalars().all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [
            {
                "id": area.id,
                "osm_id": area.osm_id,
                "admin_level": area.admin_level,
                "level_name": area.level_name,
                "name": area.name,
                "name_en": area.name_en,
                "name_vi": area.name_vi,
                "population": area.population,
                "area_km2": area.area_km2,
                "parent_id": area.parent_id
            }
            for area in areas
        ]
    }


@router.get("/admin-areas/{area_id}", response_model=Dict[str, Any])
async def get_administrative_area_detail(
    area_id: int,
    include_geometry: bool = Query(False, description="Include full boundary geometry (may be large)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific administrative area.
    
    Use include_geometry=true to get full boundary polygon (warning: can be large).
    """
    query = select(AdministrativeArea).where(AdministrativeArea.id == area_id)
    result = await db.execute(query)
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(status_code=404, detail=f"Administrative area {area_id} not found")
    
    # Get children count
    children_query = select(func.count()).where(AdministrativeArea.parent_id == area_id)
    children_count = (await db.execute(children_query)).scalar()
    
    # Get facilities count
    facilities_query = select(func.count()).where(Facility.admin_area_id == area_id)
    facilities_count = (await db.execute(facilities_query)).scalar()
    
    data = {
        "id": area.id,
        "osm_id": area.osm_id,
        "osm_type": area.osm_type,
        "admin_level": area.admin_level,
        "level_name": area.level_name,
        "name": area.name,
        "name_en": area.name_en,
        "name_vi": area.name_vi,
        "population": area.population,
        "area_km2": area.area_km2,
        "parent_id": area.parent_id,
        "children_count": children_count,
        "facilities_count": facilities_count,
        "tags": area.tags,
        "created_at": area.created_at.isoformat() if area.created_at else None,
        "updated_at": area.updated_at.isoformat() if area.updated_at else None
    }
    
    # Add center point (always)
    if area.center_point:
        center_geojson = json.loads(await db.scalar(ST_AsGeoJSON(area.center_point)))
        data["center"] = center_geojson
    
    # Add full geometry if requested
    if include_geometry and area.geometry:
        geometry_geojson = json.loads(await db.scalar(ST_AsGeoJSON(area.geometry)))
        data["geometry"] = geometry_geojson
    
    return data


@router.get("/admin-areas/hierarchy/tree", response_model=Dict[str, Any])
async def get_admin_hierarchy_tree(
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete administrative hierarchy as nested tree structure.
    City → Districts → Wards
    """
    # Get city (admin_level 4)
    city_query = select(AdministrativeArea).where(AdministrativeArea.admin_level == 4)
    city_result = await db.execute(city_query)
    city = city_result.scalar_one_or_none()
    
    if not city:
        return {"error": "Hanoi city not found in database"}
    
    # Get all districts (admin_level 6)
    districts_query = select(AdministrativeArea).where(
        AdministrativeArea.admin_level == 6
    ).order_by(AdministrativeArea.name)
    districts_result = await db.execute(districts_query)
    districts = districts_result.scalars().all()
    
    # Get all wards (admin_level 8)
    wards_query = select(AdministrativeArea).where(
        AdministrativeArea.admin_level == 8
    ).order_by(AdministrativeArea.name)
    wards_result = await db.execute(wards_query)
    wards = wards_result.scalars().all()
    
    # Build tree structure
    tree = {
        "city": {
            "id": city.id,
            "name": city.name,
            "name_vi": city.name_vi,
            "population": city.population,
            "area_km2": city.area_km2
        },
        "statistics": {
            "total_districts": len(districts),
            "total_wards": len(wards)
        },
        "districts": [
            {
                "id": district.id,
                "name": district.name,
                "name_vi": district.name_vi,
                "population": district.population,
                "wards_count": len([w for w in wards if w.parent_id == district.id])
            }
            for district in districts
        ]
    }
    
    return tree


@router.get("/facilities", response_model=Dict[str, Any])
async def get_facilities(
    category: Optional[str] = Query(None, description="Filter by category (healthcare, education, etc.)"),
    amenity: Optional[str] = Query(None, description="Filter by amenity type (hospital, school, etc.)"),
    admin_area_id: Optional[int] = Query(None, description="Filter by administrative area"),
    search: Optional[str] = Query(None, description="Search in name"),
    lat: Optional[float] = Query(None, description="Latitude for proximity search"),
    lon: Optional[float] = Query(None, description="Longitude for proximity search"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get facilities with multiple filtering options.
    
    Filters:
    - category: healthcare, education, parks, sports, culture, public_services, etc.
    - amenity: hospital, school, park, etc.
    - admin_area_id: Within specific district or ward
    - search: Text search in name
    - lat/lon + radius_km: Proximity search
    """
    query = select(Facility)
    
    if category:
        query = query.where(Facility.category == category)
    
    if amenity:
        query = query.where(Facility.amenity == amenity)
    
    if admin_area_id:
        query = query.where(Facility.admin_area_id == admin_area_id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Facility.name.ilike(search_pattern)) |
            (Facility.name_vi.ilike(search_pattern)) |
            (Facility.name_en.ilike(search_pattern))
        )
    
    # Proximity search
    if lat and lon and radius_km:
        # Create point from lat/lon
        point_wkt = f"SRID=4326;POINT({lon} {lat})"
        # Convert km to degrees (approximate)
        radius_deg = radius_km / 111.0
        query = query.where(
            ST_DWithin(Facility.location, point_wkt, radius_deg)
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get paginated results
    query = query.limit(limit).offset(offset).order_by(Facility.name)
    result = await db.execute(query)
    facilities = result.scalars().all()
    
    # Build response data
    data = []
    for facility in facilities:
        location_geojson = None
        if facility.location:
            location_geojson = json.loads(await db.scalar(ST_AsGeoJSON(facility.location)))
        
        data.append({
            "id": facility.id,
            "osm_id": facility.osm_id,
            "category": facility.category,
            "amenity": facility.amenity,
            "name": facility.name,
            "name_vi": facility.name_vi,
            "address": facility.full_address,
            "phone": facility.phone,
            "website": facility.website,
            "opening_hours": facility.opening_hours,
            "admin_area_id": facility.admin_area_id,
            "location": location_geojson
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": data
    }


@router.get("/facilities/categories", response_model=Dict[str, Any])
async def get_facilities_by_category(
    db: AsyncSession = Depends(get_db)
):
    """
    Get facility counts grouped by category.
    """
    # Query to count facilities by category
    query = select(
        Facility.category,
        func.count(Facility.id).label('count')
    ).group_by(Facility.category).order_by(func.count(Facility.id).desc())
    
    result = await db.execute(query)
    categories = result.all()
    
    return {
        "total_categories": len(categories),
        "total_facilities": sum(cat.count for cat in categories),
        "categories": [
            {
                "category": cat.category,
                "count": cat.count
            }
            for cat in categories
        ]
    }


@router.get("/facilities/{facility_id}", response_model=Dict[str, Any])
async def get_facility_detail(
    facility_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific facility.
    """
    query = select(Facility).where(Facility.id == facility_id)
    result = await db.execute(query)
    facility = result.scalar_one_or_none()
    
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")
    
    # Get admin area info if exists
    admin_area = None
    if facility.admin_area_id:
        area_query = select(AdministrativeArea).where(AdministrativeArea.id == facility.admin_area_id)
        area_result = await db.execute(area_query)
        area = area_result.scalar_one_or_none()
        if area:
            admin_area = {
                "id": area.id,
                "name": area.name,
                "name_vi": area.name_vi,
                "level_name": area.level_name
            }
    
    return {
        "id": facility.id,
        "osm_id": facility.osm_id,
        "osm_type": facility.osm_type,
        "category": facility.category,
        "amenity": facility.amenity,
        "name": facility.name,
        "name_en": facility.name_en,
        "name_vi": facility.name_vi,
        "address": {
            "street": facility.address_street,
            "district": facility.address_district,
            "city": facility.address_city,
            "full": facility.full_address
        },
        "contact": {
            "phone": facility.phone,
            "website": facility.website
        },
        "opening_hours": facility.opening_hours,
        "admin_area": admin_area,
        "location": json.loads(await db.scalar(ST_AsGeoJSON(facility.location))) if facility.location else None,
        "tags": facility.tags,
        "created_at": facility.created_at.isoformat() if facility.created_at else None,
        "updated_at": facility.updated_at.isoformat() if facility.updated_at else None
    }


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_database_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview statistics of the OSM database.
    """
    # Count administrative areas by level
    admin_stats_query = select(
        AdministrativeArea.admin_level,
        func.count(AdministrativeArea.id).label('count')
    ).group_by(AdministrativeArea.admin_level)
    admin_result = await db.execute(admin_stats_query)
    admin_stats = {row.admin_level: row.count for row in admin_result}
    
    # Count facilities by category
    facility_stats_query = select(
        Facility.category,
        func.count(Facility.id).label('count')
    ).group_by(Facility.category)
    facility_result = await db.execute(facility_stats_query)
    facility_stats = {row.category: row.count for row in facility_result}
    
    return {
        "administrative_areas": {
            "total": sum(admin_stats.values()),
            "by_level": {
                "city": admin_stats.get(4, 0),
                "districts": admin_stats.get(6, 0),
                "wards": admin_stats.get(8, 0)
            }
        },
        "facilities": {
            "total": sum(facility_stats.values()),
            "by_category": facility_stats
        }
    }
