# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Geographic API endpoints - Administrative boundaries, streets, buildings, POIs
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
from geoalchemy2.functions import ST_AsGeoJSON, ST_Simplify, ST_Contains, ST_GeomFromText, ST_DWithin, ST_Distance, ST_MakeEnvelope

from app.core.database import get_db
from app.models.geographic import AdministrativeBoundary, Street, Building, POI
from app.schemas.geographic import (
    StreetsListResponse, StreetResponse, StreetGeoJSON,
    BuildingsListResponse, BuildingResponse, BuildingGeoJSON,
    POIsListResponse, POIResponse, POIGeoJSON,
    GeoJSONFeatureCollection
)

router = APIRouter(prefix="/geographic", tags=["Geographic"])


@router.get("/boundaries/geojson")
async def get_boundaries_geojson(
    admin_level: Optional[int] = Query(None, description="Filter by admin level (4=city, 6=district, 8=ward)"),
    parent_id: Optional[int] = Query(None, description="Filter by parent boundary ID"),
    simplify_tolerance: Optional[float] = Query(0.001, description="Geometry simplification tolerance (degrees)"),
    districts_only: Optional[bool] = Query(False, description="Return only district-level boundaries"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get administrative boundaries as GeoJSON FeatureCollection.
    
    Vietnam administrative structure (post-2024 reform):
    - **admin_level**: 4 (city: Hà Nội), 6 (wards/communes: 200 units)
    - **parent_id**: Filter by parent boundary (always city for wards)
    - **simplify_tolerance**: Simplify geometry (0.001-0.01 recommended)
    - **districts_only**: DEPRECATED - use admin_level=6 for wards
    
    Note: District level (6) removed in administrative reform
    """
    
    try:
        import json
        
        # Build WHERE clause
        where_clauses = ["geometry IS NOT NULL"]  # Only return boundaries with geometry
        if districts_only:
            where_clauses.append("admin_level = 6")
        elif admin_level:
            where_clauses.append(f"admin_level = {admin_level}")
        
        if parent_id:
            where_clauses.append(f"parent_id = {parent_id}")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        # Raw SQL query with PostGIS functions
        sql_text = f"""
            SELECT 
                id, osm_id, name, name_en, admin_level, parent_id, 
                population, tags,
                ST_AsGeoJSON(ST_Simplify(geometry, {simplify_tolerance})) as geom
            FROM administrative_boundaries
            {where_sql}
        """
        
        result = await db.execute(text(sql_text))
        results = result.fetchall()
        
        # Build GeoJSON FeatureCollection
        features = []
        for row in results:
            geometry = json.loads(row.geom) if row.geom else None
            
            props = {
                "id": row.id,
                "osm_id": row.osm_id,
                "name": row.name,
                "name_en": row.name_en,
                "admin_level": row.admin_level,
                "parent_id": row.parent_id,
                "population": row.population
            }
            
            # Add OSM tags if exists
            if row.tags:
                props["tags"] = row.tags
            
            feature = {
                "type": "Feature",
                "id": row.id,
                "geometry": geometry,
                "properties": props
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "count": len(features),
                "admin_level": admin_level,
                "simplify_tolerance": simplify_tolerance
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries/hanoi-union")
async def get_hanoi_union_boundary(
    simplify_tolerance: Optional[float] = Query(0.0005, description="Geometry simplification tolerance"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Hanoi boundary as union of all ward/commune boundaries.
    
    Trả về ranh giới Hà Nội chính xác bằng cách union tất cả các phường/xã.
    Boundary này sẽ ôm sát theo ranh giới các xã/phường thay vì boundary level 4.
    
    - **simplify_tolerance**: Simplify geometry (0.0005 recommended for smooth boundary)
    
    Returns GeoJSON Feature with Hanoi boundary polygon.
    """
    try:
        import json
        
        # Union all ward/commune boundaries (admin_level = 6) that have geometry
        sql_text = f"""
            WITH hanoi_wards AS (
                SELECT geometry 
                FROM administrative_boundaries 
                WHERE admin_level = 6 
                  AND geometry IS NOT NULL
            ),
            union_geom AS (
                SELECT ST_Union(geometry) as geom FROM hanoi_wards
            )
            SELECT 
                ST_AsGeoJSON(
                    ST_Simplify(geom, {simplify_tolerance})
                ) as geojson,
                ST_Area(geom::geography) / 1000000 as area_km2,
                ST_NPoints(geom) as num_points,
                (SELECT COUNT(*) FROM hanoi_wards) as num_wards
            FROM union_geom
        """
        
        result = await db.execute(text(sql_text))
        row = result.fetchone()
        
        if not row or not row.geojson:
            raise HTTPException(status_code=404, detail="No Hanoi boundaries found")
        
        geometry = json.loads(row.geojson)
        
        return {
            "type": "Feature",
            "id": "hanoi-union",
            "geometry": geometry,
            "properties": {
                "name": "Thành phố Hà Nội",
                "name_en": "Hanoi City",
                "description": "Union boundary of all wards/communes",
                "area_km2": round(row.area_km2, 2),
                "num_points": row.num_points,
                "num_wards": row.num_wards,
                "simplify_tolerance": simplify_tolerance
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries")
async def get_boundaries(
    admin_level: Optional[int] = Query(None),
    parent_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search by name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get administrative boundaries list (without full geometry).
    """
    
    try:
        query = select(AdministrativeBoundary)
        
        if admin_level:
            query = query.where(AdministrativeBoundary.admin_level == admin_level)
        
        if parent_id:
            query = query.where(AdministrativeBoundary.parent_id == parent_id)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (AdministrativeBoundary.name.ilike(search_pattern)) |
                (AdministrativeBoundary.name_en.ilike(search_pattern))
            )
        
        total_result = await db.execute(select(func.count()).select_from(AdministrativeBoundary))
        total = total_result.scalar()
        result = await db.execute(query.offset(skip).limit(limit))
        boundaries = result.scalars().all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [
                {
                    "id": b.id,
                    "osm_id": b.osm_id,
                    "name": b.name,
                    "name_en": b.name_en,
                    "admin_level": b.admin_level,
                    "parent_id": b.parent_id,
                    "population": b.population
                }
                for b in boundaries
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries/containing-point")
async def get_boundary_containing_point(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    admin_level: Optional[int] = Query(None, description="Filter by admin level"),
    db: AsyncSession = Depends(get_db)
):
    """
    Find administrative boundary containing a point (latitude, longitude).
    """
    lat = latitude
    lng = longitude
    
    try:
        # Create point geometry
        point_wkt = f"POINT({lng} {lat})"
        
        query = select(AdministrativeBoundary).where(
            ST_Contains(
                AdministrativeBoundary.geometry,
                ST_GeomFromText(point_wkt, 4326)
            )
        )
        
        if admin_level:
            query = query.where(AdministrativeBoundary.admin_level == admin_level)
        
        result = await db.execute(query)
        boundaries = result.scalars().all()
        
        return {
            "point": {"latitude": lat, "longitude": lng},
            "boundaries": [
                {
                    "id": b.id,
                    "name": b.name,
                    "name_en": b.name_en,
                    "admin_level": b.admin_level,
                    "parent_id": b.parent_id
                }
                for b in boundaries
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries/{boundary_id}")
async def get_boundary_by_id(
    boundary_id: int,
    include_geometry: bool = Query(False, description="Include full geometry in response"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single administrative boundary by ID.
    """
    
    try:
        import json
        
        if include_geometry:
            query = select(
                AdministrativeBoundary,
                ST_AsGeoJSON(AdministrativeBoundary.geometry).label('geometry')
            ).where(AdministrativeBoundary.id == boundary_id)
            
            result = await db.execute(query)
            row = result.first()
            
            if not row:
                raise HTTPException(status_code=404, detail="Boundary not found")
            
            boundary, geometry_json = row
            geom = json.loads(await db.scalar(select(geometry_json))) if geometry_json else None
            
            return {
                "id": boundary.id,
                "osm_id": boundary.osm_id,
                "name": boundary.name,
                "name_en": boundary.name_en,
                "admin_level": boundary.admin_level,
                "parent_id": boundary.parent_id,
                "population": boundary.population,
                "tags": boundary.tags,
                "geometry": geom
            }
        else:
            query = select(AdministrativeBoundary).where(AdministrativeBoundary.id == boundary_id)
            result = await db.execute(query)
            boundary = result.scalar_one_or_none()
            
            if not boundary:
                raise HTTPException(status_code=404, detail="Boundary not found")
            
            return {
                "id": boundary.id,
                "osm_id": boundary.osm_id,
                "name": boundary.name,
                "name_en": boundary.name_en,
                "admin_level": boundary.admin_level,
                "parent_id": boundary.parent_id,
                "population": boundary.population,
                "tags": boundary.tags
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries/{boundary_id}/details")
async def get_boundary_details(
    boundary_id: int,
    include_geometry: bool = Query(True, description="Include geometry in response"),
    simplify_tolerance: float = Query(0.0005, description="Geometry simplification tolerance"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information for a single boundary including:
    - Basic info (name, area, population)
    - POIs within the boundary
    - Buildings count
    - Streets count
    - Reports within the boundary (if any)
    
    Use this endpoint to display comprehensive info panel for selected ward/commune.
    """
    import json
    
    try:
        # Get boundary basic info with geometry and area
        sql_basic = text("""
            SELECT 
                id, osm_id, osm_type, name, name_en, admin_level, parent_id,
                population, tags,
                ROUND((ST_Area(geometry::geography)/1000000)::numeric, 2) as area_km2,
                ST_AsGeoJSON(ST_Simplify(geometry, :tolerance)) as geojson,
                ST_X(ST_Centroid(geometry)) as center_lng,
                ST_Y(ST_Centroid(geometry)) as center_lat
            FROM administrative_boundaries
            WHERE id = :boundary_id AND geometry IS NOT NULL
        """)
        
        result = await db.execute(sql_basic, {"boundary_id": boundary_id, "tolerance": simplify_tolerance})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Boundary not found")
        
        boundary_info = {
            "id": row.id,
            "osm_id": row.osm_id,
            "osm_type": row.osm_type,
            "name": row.name,
            "name_en": row.name_en,
            "admin_level": row.admin_level,
            "parent_id": row.parent_id,
            "population": row.population,
            "tags": row.tags if row.tags else {},
            "area_km2": float(row.area_km2) if row.area_km2 else 0,
            "center": {"lat": row.center_lat, "lng": row.center_lng}
        }
        
        if include_geometry and row.geojson:
            boundary_info["geometry"] = json.loads(row.geojson)
        
        # Get POIs within boundary
        sql_pois = text("""
            SELECT 
                SUM(cnt) as total,
                COUNT(*) as category_types,
                jsonb_object_agg(
                    COALESCE(category, 'other'), 
                    cnt
                ) as by_category
            FROM (
                SELECT category, COUNT(*) as cnt
                FROM pois p, administrative_boundaries b
                WHERE b.id = :boundary_id 
                  AND ST_Contains(b.geometry, p.location)
                GROUP BY category
            ) sub
        """)
        
        pois_result = await db.execute(sql_pois, {"boundary_id": boundary_id})
        pois_row = pois_result.fetchone()
        
        pois_stats = {
            "total": pois_row.total if pois_row and pois_row.total else 0,
            "category_types": pois_row.category_types if pois_row and pois_row.category_types else 0,
            "by_category": pois_row.by_category if pois_row and pois_row.by_category else {}
        }
        
        # Get top POIs with names and contact info
        sql_top_pois = text("""
            SELECT p.id, p.name, p.category, p.subcategory, p.address,
                   p.phone, p.website, p.opening_hours,
                   ST_X(p.location) as lng, ST_Y(p.location) as lat
            FROM pois p, administrative_boundaries b
            WHERE b.id = :boundary_id 
              AND ST_Contains(b.geometry, p.location)
              AND p.name IS NOT NULL
            ORDER BY 
                CASE 
                    WHEN p.category IN ('healthcare', 'education', 'government') THEN 1
                    WHEN p.category IN ('finance', 'shop') THEN 2
                    ELSE 3
                END,
                p.name
            LIMIT 30
        """)
        
        top_pois_result = await db.execute(sql_top_pois, {"boundary_id": boundary_id})
        top_pois = [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "subcategory": r.subcategory,
                "address": r.address,
                "phone": r.phone,
                "website": r.website,
                "opening_hours": r.opening_hours,
                "location": {"lat": r.lat, "lng": r.lng}
            }
            for r in top_pois_result.fetchall()
        ]
        
        # Get subcategory breakdown
        sql_subcategory = text("""
            SELECT category, subcategory, COUNT(*) as cnt
            FROM pois p, administrative_boundaries b
            WHERE b.id = :boundary_id 
              AND ST_Contains(b.geometry, p.location)
            GROUP BY category, subcategory
            ORDER BY category, cnt DESC
        """)
        
        subcategory_result = await db.execute(sql_subcategory, {"boundary_id": boundary_id})
        by_subcategory = {}
        for r in subcategory_result.fetchall():
            cat = r.category or 'other'
            subcat = r.subcategory or 'other'
            if cat not in by_subcategory:
                by_subcategory[cat] = {}
            by_subcategory[cat][subcat] = r.cnt
        
        pois_stats["by_subcategory"] = by_subcategory
        
        # Get buildings count within boundary
        sql_buildings = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN b.name IS NOT NULL THEN 1 END) as named
            FROM buildings b, administrative_boundaries ab
            WHERE ab.id = :boundary_id 
              AND ST_Contains(ab.geometry, ST_Centroid(b.geometry))
        """)
        
        buildings_result = await db.execute(sql_buildings, {"boundary_id": boundary_id})
        buildings_row = buildings_result.fetchone()
        
        buildings_stats = {
            "total": buildings_row.total if buildings_row else 0,
            "named": buildings_row.named if buildings_row else 0
        }
        
        # Get streets within boundary
        sql_streets = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN s.name IS NOT NULL THEN 1 END) as named,
                COUNT(DISTINCT highway_type) as highway_types
            FROM streets s, administrative_boundaries b
            WHERE b.id = :boundary_id 
              AND ST_Intersects(b.geometry, s.geometry)
        """)
        
        streets_result = await db.execute(sql_streets, {"boundary_id": boundary_id})
        streets_row = streets_result.fetchone()
        
        streets_stats = {
            "total": streets_row.total if streets_row else 0,
            "named": streets_row.named if streets_row else 0,
            "highway_types": streets_row.highway_types if streets_row else 0
        }
        
        # Get street types breakdown
        sql_street_types = text("""
            SELECT highway_type, COUNT(*) as cnt
            FROM streets s, administrative_boundaries b
            WHERE b.id = :boundary_id 
              AND ST_Intersects(b.geometry, s.geometry)
            GROUP BY highway_type
            ORDER BY cnt DESC
        """)
        
        street_types_result = await db.execute(sql_street_types, {"boundary_id": boundary_id})
        by_highway_type = {r.highway_type: r.cnt for r in street_types_result.fetchall() if r.highway_type}
        streets_stats["by_highway_type"] = by_highway_type
        
        # Get top named streets
        sql_top_streets = text("""
            SELECT DISTINCT s.name, s.highway_type,
                   ROUND(ST_Length(ST_Intersection(s.geometry, b.geometry)::geography)::numeric) as length_m
            FROM streets s, administrative_boundaries b
            WHERE b.id = :boundary_id 
              AND ST_Intersects(b.geometry, s.geometry)
              AND s.name IS NOT NULL
            ORDER BY length_m DESC
            LIMIT 15
        """)
        
        top_streets_result = await db.execute(sql_top_streets, {"boundary_id": boundary_id})
        top_streets = [
            {"name": r.name, "highway_type": r.highway_type, "length_m": int(r.length_m) if r.length_m else 0}
            for r in top_streets_result.fetchall()
        ]
        streets_stats["top_streets"] = top_streets
        
        # Try to get reports if table exists
        reports_stats = {"total": 0, "by_status": {}, "by_category": {}}
        try:
            sql_reports = text("""
                SELECT 
                    COUNT(*) as total,
                    jsonb_object_agg(COALESCE(status, 'unknown'), cnt) as by_status
                FROM (
                    SELECT status, COUNT(*) as cnt
                    FROM reports r, administrative_boundaries b
                    WHERE b.id = :boundary_id 
                      AND ST_Contains(b.geometry, r.location)
                    GROUP BY status
                ) sub
            """)
            reports_result = await db.execute(sql_reports, {"boundary_id": boundary_id})
            reports_row = reports_result.fetchone()
            if reports_row and reports_row.total:
                reports_stats = {
                    "total": reports_row.total,
                    "by_status": reports_row.by_status or {}
                }
        except:
            pass  # Reports table might not exist
        
        return {
            "boundary": boundary_info,
            "statistics": {
                "pois": pois_stats,
                "top_pois": top_pois,
                "buildings": buildings_stats,
                "streets": streets_stats,
                "reports": reports_stats
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/boundaries/list/simple")
async def get_boundaries_list_simple(
    admin_level: int = Query(6, description="Admin level (6 = ward/commune)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get simple list of boundaries for dropdown/selection.
    Returns only id, name, and area - optimized for UI components.
    """
    try:
        sql = text("""
            SELECT 
                id, name, name_en,
                ROUND((ST_Area(geometry::geography)/1000000)::numeric, 2) as area_km2
            FROM administrative_boundaries
            WHERE admin_level = :admin_level AND geometry IS NOT NULL
            ORDER BY name
        """)
        
        result = await db.execute(sql, {"admin_level": admin_level})
        rows = result.fetchall()
        
        return {
            "total": len(rows),
            "items": [
                {
                    "id": r.id,
                    "name": r.name,
                    "name_en": r.name_en,
                    "area_km2": float(r.area_km2) if r.area_km2 else 0
                }
                for r in rows
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/boundaries/multi-details")
async def get_multi_boundaries_details(
    boundary_ids: List[int],
    include_geometry: bool = Query(True, description="Include geometry"),
    simplify_tolerance: float = Query(0.001, description="Geometry simplification"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details for multiple boundaries at once.
    Useful for comparing or displaying multiple selected wards/communes.
    
    Request body: List of boundary IDs
    """
    import json
    
    if not boundary_ids:
        raise HTTPException(status_code=400, detail="boundary_ids cannot be empty")
    
    if len(boundary_ids) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 boundaries at once")
    
    try:
        # Convert list to tuple for SQL
        ids_tuple = tuple(boundary_ids)
        
        sql = text(f"""
            SELECT 
                id, osm_id, name, name_en, admin_level,
                population, tags,
                ROUND((ST_Area(geometry::geography)/1000000)::numeric, 2) as area_km2,
                ST_AsGeoJSON(ST_Simplify(geometry, :tolerance)) as geojson,
                ST_X(ST_Centroid(geometry)) as center_lng,
                ST_Y(ST_Centroid(geometry)) as center_lat
            FROM administrative_boundaries
            WHERE id = ANY(:ids) AND geometry IS NOT NULL
            ORDER BY name
        """)
        
        result = await db.execute(sql, {"ids": list(boundary_ids), "tolerance": simplify_tolerance})
        rows = result.fetchall()
        
        boundaries = []
        total_area = 0
        total_population = 0
        
        for row in rows:
            boundary = {
                "id": row.id,
                "osm_id": row.osm_id,
                "name": row.name,
                "name_en": row.name_en,
                "admin_level": row.admin_level,
                "population": row.population,
                "tags": row.tags if row.tags else {},
                "area_km2": float(row.area_km2) if row.area_km2 else 0,
                "center": {"lat": row.center_lat, "lng": row.center_lng}
            }
            
            if include_geometry and row.geojson:
                boundary["geometry"] = json.loads(row.geojson)
            
            boundaries.append(boundary)
            total_area += boundary["area_km2"]
            if row.population:
                total_population += row.population
        
        # Get combined statistics for all selected boundaries
        sql_pois = text("""
            SELECT COUNT(*) as total
            FROM pois p, administrative_boundaries b
            WHERE b.id = ANY(:ids) AND ST_Contains(b.geometry, p.location)
        """)
        pois_result = await db.execute(sql_pois, {"ids": list(boundary_ids)})
        pois_count = pois_result.scalar() or 0
        
        return {
            "boundaries": boundaries,
            "summary": {
                "count": len(boundaries),
                "total_area_km2": round(total_area, 2),
                "total_population": total_population,
                "total_pois": pois_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================================
# STREETS API
# ============================================================================

@router.get("/streets", response_model=StreetsListResponse)
async def get_streets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by street name"),
    highway_type: Optional[str] = Query(None, description="Filter by highway type (primary, secondary, residential, etc.)"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    has_name: Optional[bool] = Query(None, description="Filter streets with/without names"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of streets in Hanoi.
    
    **Highway types:** primary, secondary, tertiary, residential, service, footway, cycleway, path, etc.
    """
    try:
        query = select(Street)
        
        # Apply filters
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Street.name.ilike(search_pattern),
                    Street.name_en.ilike(search_pattern)
                )
            )
        
        if highway_type:
            filters.append(Street.highway_type == highway_type)
        
        if district_id:
            filters.append(Street.district_id == district_id)
        
        if has_name is not None:
            if has_name:
                filters.append(Street.name.isnot(None))
            else:
                filters.append(Street.name.is_(None))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        total_query = select(func.count()).select_from(Street)
        if filters:
            total_query = total_query.where(and_(*filters))
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Street.id)
        result = await db.execute(query)
        streets = result.scalars().all()
        
        return StreetsListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[StreetResponse.from_orm(s) for s in streets]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/streets/geojson", response_model=GeoJSONFeatureCollection)
async def get_streets_geojson(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    highway_type: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="Bounding box: minLon,minLat,maxLon,maxLat"),
    simplify: Optional[float] = Query(0.0001, ge=0, le=0.01, description="Geometry simplification tolerance"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get streets as GeoJSON FeatureCollection.
    
    **bbox format:** `105.8,21.0,105.9,21.1` (minLon,minLat,maxLon,maxLat)
    """
    try:
        import json
        
        # Build WHERE clause
        where_clauses = []
        if search:
            where_clauses.append(f"(name ILIKE '%{search}%' OR name_en ILIKE '%{search}%')")
        if highway_type:
            where_clauses.append(f"highway_type = '{highway_type}'")
        if bbox:
            coords = [float(x) for x in bbox.split(',')]
            if len(coords) == 4:
                min_lon, min_lat, max_lon, max_lat = coords
                where_clauses.append(
                    f"geometry && ST_MakeEnvelope({min_lon}, {min_lat}, {max_lon}, {max_lat}, 4326)"
                )
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql_text = f"""
            SELECT 
                id, osm_id, name, name_en, highway_type, surface, lanes, 
                maxspeed, oneway, length, tags,
                ST_AsGeoJSON(ST_Simplify(geometry, {simplify})) as geom
            FROM streets
            {where_sql}
            ORDER BY id
            LIMIT {limit} OFFSET {skip}
        """
        
        result = await db.execute(text(sql_text))
        rows = result.fetchall()
        
        features = []
        for row in rows:
            geometry = json.loads(row.geom) if row.geom else None
            
            feature = {
                "type": "Feature",
                "id": row.id,
                "geometry": geometry,
                "properties": {
                    "id": row.id,
                    "osm_id": row.osm_id,
                    "name": row.name,
                    "name_en": row.name_en,
                    "highway_type": row.highway_type,
                    "surface": row.surface,
                    "lanes": row.lanes,
                    "maxspeed": row.maxspeed,
                    "oneway": row.oneway,
                    "length": float(row.length) if row.length else None
                }
            }
            features.append(feature)
        
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features,
            metadata={"count": len(features), "skip": skip, "limit": limit}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/streets/types", response_model=List[dict])
async def get_street_types(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unique highway types and their counts.
    """
    try:
        query = text("""
            SELECT highway_type, COUNT(*) as count
            FROM streets
            WHERE highway_type IS NOT NULL
            GROUP BY highway_type
            ORDER BY count DESC
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [{"type": row.highway_type, "count": row.count} for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/streets/nearby", response_model=StreetsListResponse)
async def get_streets_nearby(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(1000, ge=0, le=10000, description="Search radius in meters"),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Find streets within radius of a point.
    """
    try:
        point_wkt = f"POINT({longitude} {latitude})"
        
        query = select(Street).where(
            ST_DWithin(
                Street.geometry,
                ST_GeomFromText(point_wkt, 4326),
                radius_meters / 111319.0  # Convert meters to degrees (approximate)
            )
        ).limit(limit)
        
        result = await db.execute(query)
        streets = result.scalars().all()
        
        return StreetsListResponse(
            total=len(streets),
            skip=0,
            limit=limit,
            items=[StreetResponse.from_orm(s) for s in streets]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/streets/{street_id}", response_model=StreetResponse)
async def get_street_by_id(
    street_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single street by ID."""
    try:
        query = select(Street).where(Street.id == street_id)
        result = await db.execute(query)
        street = result.scalar_one_or_none()
        
        if not street:
            raise HTTPException(status_code=404, detail="Street not found")
        
        return StreetResponse.from_orm(street)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================================
# BUILDINGS API
# ============================================================================

@router.get("/buildings", response_model=BuildingsListResponse)
async def get_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by building name or address"),
    building_type: Optional[str] = Query(None, description="Filter by building type"),
    district_id: Optional[int] = Query(None),
    has_name: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of buildings in Hanoi.
    
    **Building types:** residential, commercial, industrial, retail, apartments, house, etc.
    """
    try:
        query = select(Building)
        
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Building.name.ilike(search_pattern),
                    Building.addr_street.ilike(search_pattern)
                )
            )
        
        if building_type:
            filters.append(Building.building_type == building_type)
        
        if district_id:
            filters.append(Building.district_id == district_id)
        
        if has_name is not None:
            if has_name:
                filters.append(Building.name.isnot(None))
            else:
                filters.append(Building.name.is_(None))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        total_query = select(func.count()).select_from(Building)
        if filters:
            total_query = total_query.where(and_(*filters))
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Building.id)
        result = await db.execute(query)
        buildings = result.scalars().all()
        
        return BuildingsListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[BuildingResponse.from_orm(b) for b in buildings]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/buildings/geojson", response_model=GeoJSONFeatureCollection)
async def get_buildings_geojson(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_type: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="Bounding box: minLon,minLat,maxLon,maxLat"),
    simplify: Optional[float] = Query(0.00001, ge=0, le=0.01),
    db: AsyncSession = Depends(get_db)
):
    """
    Get buildings as GeoJSON FeatureCollection.
    """
    try:
        import json
        
        where_clauses = []
        if building_type:
            where_clauses.append(f"building_type = '{building_type}'")
        if bbox:
            coords = [float(x) for x in bbox.split(',')]
            if len(coords) == 4:
                min_lon, min_lat, max_lon, max_lat = coords
                where_clauses.append(
                    f"geometry && ST_MakeEnvelope({min_lon}, {min_lat}, {max_lon}, {max_lat}, 4326)"
                )
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql_text = f"""
            SELECT 
                id, osm_id, name, building_type, addr_housenumber, addr_street,
                addr_district, levels, height, area, tags,
                ST_AsGeoJSON(ST_Simplify(geometry, {simplify})) as geom
            FROM buildings
            {where_sql}
            ORDER BY id
            LIMIT {limit} OFFSET {skip}
        """
        
        result = await db.execute(text(sql_text))
        rows = result.fetchall()
        
        features = []
        for row in rows:
            geometry = json.loads(row.geom) if row.geom else None
            
            feature = {
                "type": "Feature",
                "id": row.id,
                "geometry": geometry,
                "properties": {
                    "id": row.id,
                    "osm_id": row.osm_id,
                    "name": row.name,
                    "building_type": row.building_type,
                    "address": {
                        "housenumber": row.addr_housenumber,
                        "street": row.addr_street,
                        "district": row.addr_district
                    },
                    "levels": row.levels,
                    "height": float(row.height) if row.height else None,
                    "area": float(row.area) if row.area else None
                }
            }
            features.append(feature)
        
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features,
            metadata={"count": len(features), "skip": skip, "limit": limit}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/buildings/types", response_model=List[dict])
async def get_building_types(
    db: AsyncSession = Depends(get_db)
):
    """Get all unique building types and their counts."""
    try:
        query = text("""
            SELECT building_type, COUNT(*) as count
            FROM buildings
            WHERE building_type IS NOT NULL
            GROUP BY building_type
            ORDER BY count DESC
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [{"type": row.building_type, "count": row.count} for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/buildings/{building_id}", response_model=BuildingResponse)
async def get_building_by_id(
    building_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single building by ID."""
    try:
        query = select(Building).where(Building.id == building_id)
        result = await db.execute(query)
        building = result.scalar_one_or_none()
        
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        return BuildingResponse.from_orm(building)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================================
# POIs API
# ============================================================================

@router.get("/pois", response_model=POIsListResponse)
async def get_pois(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by POI name"),
    category: Optional[str] = Query(None, description="Filter by category (amenity, shop, tourism, etc.)"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    district_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of Points of Interest (POIs) in Hanoi.
    
    **Categories:** amenity, shop, tourism, leisure, office, healthcare, education, etc.
    **Amenity subcategories:** restaurant, cafe, bank, school, hospital, pharmacy, etc.
    **Shop subcategories:** supermarket, convenience, mall, bakery, etc.
    """
    try:
        query = select(POI)
        
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    POI.name.ilike(search_pattern),
                    POI.name_en.ilike(search_pattern)
                )
            )
        
        if category:
            filters.append(POI.category == category)
        
        if subcategory:
            filters.append(POI.subcategory == subcategory)
        
        if district_id:
            filters.append(POI.district_id == district_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        total_query = select(func.count()).select_from(POI)
        if filters:
            total_query = total_query.where(and_(*filters))
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(POI.id)
        result = await db.execute(query)
        pois = result.scalars().all()
        
        return POIsListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[POIResponse.from_orm(p) for p in pois]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pois/geojson", response_model=GeoJSONFeatureCollection)
async def get_pois_geojson(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    bbox: Optional[str] = Query(None, description="Bounding box: minLon,minLat,maxLon,maxLat"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get POIs as GeoJSON FeatureCollection.
    """
    try:
        import json
        
        where_clauses = []
        if category:
            where_clauses.append(f"category = '{category}'")
        if subcategory:
            where_clauses.append(f"subcategory = '{subcategory}'")
        if bbox:
            coords = [float(x) for x in bbox.split(',')]
            if len(coords) == 4:
                min_lon, min_lat, max_lon, max_lat = coords
                where_clauses.append(
                    f"location && ST_MakeEnvelope({min_lon}, {min_lat}, {max_lon}, {max_lat}, 4326)"
                )
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql_text = f"""
            SELECT 
                id, osm_id, name, name_en, category, subcategory,
                address, phone, website, email,
                opening_hours, tags,
                ST_AsGeoJSON(location) as geom
            FROM pois
            {where_sql}
            ORDER BY id
            LIMIT {limit} OFFSET {skip}
        """
        
        result = await db.execute(text(sql_text))
        rows = result.fetchall()
        
        features = []
        for row in rows:
            geometry = json.loads(row.geom) if row.geom else None
            
            feature = {
                "type": "Feature",
                "id": row.id,
                "geometry": geometry,
                "properties": {
                    "id": row.id,
                    "osm_id": row.osm_id,
                    "name": row.name,
                    "name_en": row.name_en,
                    "category": row.category,
                    "subcategory": row.subcategory,
                    "address": row.address,
                    "contact": {
                        "phone": row.phone,
                        "website": row.website,
                        "email": row.email
                    },
                    "opening_hours": row.opening_hours
                }
            }
            features.append(feature)
        
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features,
            metadata={"count": len(features), "skip": skip, "limit": limit}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pois/categories", response_model=List[dict])
async def get_poi_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all unique POI categories and subcategories with counts."""
    try:
        query = text("""
            SELECT 
                category, 
                subcategory, 
                COUNT(*) as count
            FROM pois
            WHERE category IS NOT NULL
            GROUP BY category, subcategory
            ORDER BY category, count DESC
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "category": row.category,
                "subcategory": row.subcategory,
                "count": row.count
            }
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pois/nearby", response_model=POIsListResponse)
async def get_pois_nearby(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(1000, ge=0, le=10000),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Find POIs within radius of a point.
    """
    try:
        point_wkt = f"POINT({longitude} {latitude})"
        
        query = select(POI).where(
            ST_DWithin(
                POI.location,
                ST_GeomFromText(point_wkt, 4326),
                radius_meters / 111319.0  # Convert meters to degrees
            )
        )
        
        if category:
            query = query.where(POI.category == category)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        pois = result.scalars().all()
        
        return POIsListResponse(
            total=len(pois),
            skip=0,
            limit=limit,
            items=[POIResponse.from_orm(p) for p in pois]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/pois/{poi_id}", response_model=POIResponse)
async def get_poi_by_id(
    poi_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single POI by ID."""
    try:
        query = select(POI).where(POI.id == poi_id)
        result = await db.execute(query)
        poi = result.scalar_one_or_none()
        
        if not poi:
            raise HTTPException(status_code=404, detail="POI not found")
        
        return POIResponse.from_orm(poi)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================================
# STATISTICS & OVERVIEW
# ============================================================================

@router.get("/statistics")
async def get_geographic_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive statistics about Hanoi's geographic data.
    """
    try:
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM administrative_boundaries WHERE admin_level = 6) as boundaries_count,
                (SELECT COUNT(*) FROM administrative_boundaries WHERE admin_level = 6 AND name LIKE 'Phường%') as phuong_count,
                (SELECT COUNT(*) FROM administrative_boundaries WHERE admin_level = 6 AND name LIKE 'Xã%') as xa_count,
                (SELECT COUNT(*) FROM streets) as streets_count,
                (SELECT COUNT(*) FROM streets WHERE name IS NOT NULL) as named_streets_count,
                (SELECT COUNT(*) FROM buildings) as buildings_count,
                (SELECT COUNT(*) FROM buildings WHERE name IS NOT NULL) as named_buildings_count,
                (SELECT COUNT(*) FROM pois) as pois_count,
                (SELECT ST_AsText(ST_Extent(geometry)) FROM streets) as streets_bbox,
                (SELECT ST_AsText(ST_Extent(geometry)) FROM buildings) as buildings_bbox,
                (SELECT ST_AsText(ST_Extent(location)) FROM pois) as pois_bbox
        """)
        
        result = await db.execute(stats_query)
        row = result.fetchone()
        
        return {
            "administrative_boundaries": {
                "total": row.boundaries_count,
                "phuong": row.phuong_count,
                "xa": row.xa_count
            },
            "streets": {
                "total": row.streets_count,
                "named": row.named_streets_count,
                "bbox": row.streets_bbox
            },
            "buildings": {
                "total": row.buildings_count,
                "named": row.named_buildings_count,
                "bbox": row.buildings_bbox
            },
            "pois": {
                "total": row.pois_count,
                "bbox": row.pois_bbox
            },
            "summary": {
                "total_features": row.boundaries_count + row.streets_count + row.buildings_count + row.pois_count,
                "data_source": "OpenStreetMap",
                "city": "Hanoi",
                "last_updated": "2025-12-07"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================================
# URBAN DATA INTEGRATION - Weather, AQI, Traffic (Real-time APIs)
# ============================================================================

@router.get("/boundaries/{boundary_id}/urban-data")
async def get_boundary_urban_data(
    boundary_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get integrated urban data for a specific boundary.
    
    Combines:
    - Weather data from OpenWeatherMap API
    - Air Quality (AQI) from AQICN/WAQI API  
    - Traffic flow from TomTom API (real-time, not stored)
    
    This endpoint provides a comprehensive urban environment overview
    for smart city analysis following LOD (Linked Open Data) principles.
    """
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get boundary centroid
    try:
        centroid_query = text("""
            SELECT 
                name,
                ST_X(ST_Centroid(geometry)) as lon,
                ST_Y(ST_Centroid(geometry)) as lat,
                ST_Area(geometry::geography) / 1000000 as area_km2
            FROM administrative_boundaries
            WHERE id = :boundary_id
        """)
        result = await db.execute(centroid_query, {"boundary_id": boundary_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Boundary not found")
        
        boundary_name = row.name
        lat = row.lat
        lon = row.lon
        area_km2 = row.area_km2
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Fetch urban data from external APIs
    weather_data = None
    aqi_data = None
    traffic_data = None
    
    # 1. Weather from OpenWeatherMap
    try:
        from app.core.config import settings
        if settings.OPENWEATHER_API_KEY:
            from app.adapters.openweathermap import OpenWeatherMapAdapter
            adapter = OpenWeatherMapAdapter()
            ngsi_entity, _ = await adapter.fetch_weather(lat, lon, boundary_name)
            weather_data = {
                "temperature": ngsi_entity.get("temperature", {}).get("value"),
                "humidity": ngsi_entity.get("humidity", {}).get("value"),
                "pressure": ngsi_entity.get("pressure", {}).get("value"),
                "wind_speed": ngsi_entity.get("windSpeed", {}).get("value"),
                "description": ngsi_entity.get("description", {}).get("value"),
                "weather_type": ngsi_entity.get("weatherType", {}).get("value"),
                "feels_like": ngsi_entity.get("feelsLikeTemperature", {}).get("value"),
                "clouds": ngsi_entity.get("clouds", {}).get("value"),
                "source": "OpenWeatherMap",
                "ngsi_ld_id": ngsi_entity.get("id")
            }
    except Exception as e:
        logger.warning(f"Weather API error: {e}")
        weather_data = _get_weather_stub_data(lat, lon, boundary_name)
    
    # 2. Air Quality from AQICN
    try:
        from app.core.config import settings
        if settings.AQICN_API_KEY:
            from app.adapters.aqicn import AQICNAdapter
            adapter = AQICNAdapter()
            ngsi_entity, _ = await adapter.fetch_geo_data(lat, lon)
            aqi_value = ngsi_entity.get("airQualityIndex", {}).get("value", 0)
            aqi_data = {
                "aqi": aqi_value,
                "level": _get_aqi_level_info(aqi_value),
                "pm25": ngsi_entity.get("pm25", {}).get("value"),
                "pm10": ngsi_entity.get("pm10", {}).get("value"),
                "o3": ngsi_entity.get("o3", {}).get("value"),
                "no2": ngsi_entity.get("no2", {}).get("value"),
                "so2": ngsi_entity.get("so2", {}).get("value"),
                "co": ngsi_entity.get("co", {}).get("value"),
                "source": "AQICN/WAQI",
                "ngsi_ld_id": ngsi_entity.get("id")
            }
    except Exception as e:
        logger.warning(f"AQI API error: {e}")
        aqi_data = _get_aqi_stub_data()
    
    # 3. Traffic from TomTom (real-time only, NOT stored in database)
    try:
        from app.core.config import settings
        if settings.TOMTOM_API_KEY:
            from app.adapters.tomtom import TomTomAdapter
            adapter = TomTomAdapter()
            ngsi_entity = await adapter.fetch_traffic_flow(lat, lon, location_name=boundary_name)
            
            current_speed = ngsi_entity.get("averageVehicleSpeed", {}).get("value", 0)
            free_flow_speed = ngsi_entity.get("averageVehicleSpeedFreeFlow", {}).get("value", 1)
            congestion = ngsi_entity.get("congestionLevel", {}).get("value", 0)
            
            traffic_data = {
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed,
                "congestion_percent": congestion,
                "congestion_level": _get_congestion_level(congestion),
                "travel_time": ngsi_entity.get("travelTime", {}).get("value"),
                "confidence": ngsi_entity.get("confidence", {}).get("value"),
                "road_closed": ngsi_entity.get("roadClosed", {}).get("value", False),
                "source": "TomTom Traffic API (real-time)",
                "ngsi_ld_id": ngsi_entity.get("id"),
                "note": "Data fetched in real-time from TomTom API, not stored in database"
            }
    except Exception as e:
        logger.warning(f"Traffic API error: {e}")
        traffic_data = _get_traffic_stub_data()
    
    # Build comprehensive response
    return {
        "boundary": {
            "id": boundary_id,
            "name": boundary_name,
            "centroid": {
                "latitude": lat,
                "longitude": lon
            },
            "area_km2": round(area_km2, 2) if area_km2 else None
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "weather": weather_data,
        "air_quality": aqi_data,
        "traffic": traffic_data,
        "lod_context": {
            "description": "Linked Open Data integration from multiple sources",
            "sources": [
                {"name": "OpenStreetMap", "type": "Geographic Foundation (Layer 1)"},
                {"name": "OpenWeatherMap", "type": "Environmental Data (Layer 2)"},
                {"name": "AQICN/WAQI", "type": "Environmental Data (Layer 2)"},
                {"name": "TomTom", "type": "Transportation Data (Layer 2, real-time only)"}
            ],
            "standards": ["NGSI-LD", "SOSA/SSN", "Smart Data Models"]
        }
    }


def _get_aqi_level_info(aqi_value: int) -> dict:
    """Get AQI level information in Vietnamese."""
    if aqi_value <= 50:
        return {
            "text": "Tốt",
            "text_en": "Good",
            "color": "#00E400",
            "health_advice": "Chất lượng không khí tốt, an toàn cho mọi hoạt động ngoài trời"
        }
    elif aqi_value <= 100:
        return {
            "text": "Trung bình",
            "text_en": "Moderate", 
            "color": "#FFFF00",
            "health_advice": "Chất lượng chấp nhận được, nhóm nhạy cảm nên hạn chế hoạt động ngoài trời kéo dài"
        }
    elif aqi_value <= 150:
        return {
            "text": "Không tốt cho nhóm nhạy cảm",
            "text_en": "Unhealthy for Sensitive Groups",
            "color": "#FF7E00",
            "health_advice": "Trẻ em, người già và người có bệnh hô hấp nên hạn chế ra ngoài"
        }
    elif aqi_value <= 200:
        return {
            "text": "Không lành mạnh",
            "text_en": "Unhealthy",
            "color": "#FF0000",
            "health_advice": "Mọi người nên hạn chế hoạt động ngoài trời, đeo khẩu trang khi ra ngoài"
        }
    elif aqi_value <= 300:
        return {
            "text": "Rất không lành mạnh",
            "text_en": "Very Unhealthy",
            "color": "#8F3F97",
            "health_advice": "Cảnh báo sức khỏe - tránh mọi hoạt động ngoài trời"
        }
    else:
        return {
            "text": "Nguy hiểm",
            "text_en": "Hazardous",
            "color": "#7E0023",
            "health_advice": "Cảnh báo khẩn cấp - ở trong nhà, đóng cửa sổ"
        }


def _get_congestion_level(congestion_percent: int) -> dict:
    """Get traffic congestion level in Vietnamese."""
    if congestion_percent <= 10:
        return {
            "text": "Thông thoáng",
            "text_en": "Free Flow",
            "color": "#00E400",
            "icon": "🟢"
        }
    elif congestion_percent <= 30:
        return {
            "text": "Nhẹ",
            "text_en": "Light",
            "color": "#FFFF00",
            "icon": "🟡"
        }
    elif congestion_percent <= 50:
        return {
            "text": "Trung bình",
            "text_en": "Moderate",
            "color": "#FF7E00",
            "icon": "🟠"
        }
    elif congestion_percent <= 70:
        return {
            "text": "Đông đúc",
            "text_en": "Heavy",
            "color": "#FF0000",
            "icon": "🔴"
        }
    else:
        return {
            "text": "Tắc nghẽn",
            "text_en": "Severe",
            "color": "#7E0023",
            "icon": "⛔"
        }


def _get_weather_stub_data(lat: float, lon: float, name: str) -> dict:
    """Return stub weather data when API is unavailable."""
    return {
        "temperature": 28.5,
        "humidity": 75,
        "pressure": 1012,
        "wind_speed": 3.5,
        "description": "Có mây",
        "weather_type": "Clouds",
        "feels_like": 30.2,
        "clouds": 40,
        "source": "stub (API unavailable)",
        "ngsi_ld_id": None
    }


def _get_aqi_stub_data() -> dict:
    """Return stub AQI data when API is unavailable."""
    return {
        "aqi": 85,
        "level": {
            "text": "Trung bình",
            "text_en": "Moderate",
            "color": "#FFFF00",
            "health_advice": "Chất lượng chấp nhận được"
        },
        "pm25": 35.0,
        "pm10": 55.0,
        "o3": 45.0,
        "no2": 20.0,
        "so2": 8.0,
        "co": 0.4,
        "source": "stub (API unavailable)",
        "ngsi_ld_id": None
    }


def _get_traffic_stub_data() -> dict:
    """Return stub traffic data when API is unavailable."""
    return {
        "current_speed": 25.0,
        "free_flow_speed": 50.0,
        "congestion_percent": 50,
        "congestion_level": {
            "text": "Trung bình",
            "text_en": "Moderate",
            "color": "#FF7E00",
            "icon": "🟠"
        },
        "travel_time": 120,
        "confidence": 0.85,
        "road_closed": False,
        "source": "stub (API unavailable)",
        "ngsi_ld_id": None,
        "note": "Stub data - TomTom API key not configured"
    }
