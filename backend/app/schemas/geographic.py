# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Geographic data schemas - Streets, Buildings, POIs, Boundaries
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json


# ============================================================================
# Administrative Boundary Schemas
# ============================================================================

class AdministrativeBoundaryBase(BaseModel):
    osm_id: int
    osm_type: str
    name: str
    name_en: Optional[str] = None
    admin_level: int
    parent_id: Optional[int] = None
    population: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None


class AdministrativeBoundaryResponse(AdministrativeBoundaryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        from_attributes = True


class AdministrativeBoundaryGeoJSON(BaseModel):
    type: str = "Feature"
    id: int
    geometry: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any]


# ============================================================================
# Street Schemas
# ============================================================================

class StreetBase(BaseModel):
    osm_id: int
    osm_type: str
    name: Optional[str] = None
    name_en: Optional[str] = None
    highway_type: Optional[str] = None
    surface: Optional[str] = None
    lanes: Optional[int] = None
    maxspeed: Optional[int] = None
    oneway: bool = False
    district_id: Optional[int] = None
    length: Optional[float] = None
    tags: Optional[Dict[str, Any]] = None


class StreetResponse(StreetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        from_attributes = True


class StreetGeoJSON(BaseModel):
    type: str = "Feature"
    id: int
    geometry: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any]


class StreetsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[StreetResponse]


# ============================================================================
# Building Schemas
# ============================================================================

class BuildingBase(BaseModel):
    osm_id: int
    osm_type: str
    name: Optional[str] = None
    building_type: Optional[str] = None
    addr_housenumber: Optional[str] = None
    addr_street: Optional[str] = None
    addr_district: Optional[str] = None
    addr_city: Optional[str] = None
    levels: Optional[int] = None
    height: Optional[float] = None
    area: Optional[float] = None
    district_id: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None


class BuildingResponse(BuildingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        from_attributes = True


class BuildingGeoJSON(BaseModel):
    type: str = "Feature"
    id: int
    geometry: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any]


class BuildingsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[BuildingResponse]


# ============================================================================
# POI Schemas
# ============================================================================

class POIBase(BaseModel):
    osm_id: int
    osm_type: str
    name: Optional[str] = None
    name_en: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    opening_hours: Optional[str] = None
    district_id: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None


class POIResponse(POIBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        from_attributes = True


class POIGeoJSON(BaseModel):
    type: str = "Feature"
    id: int
    geometry: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any]


class POIsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[POIResponse]


# ============================================================================
# GeoJSON Collection Schemas
# ============================================================================

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Query Schemas
# ============================================================================

class BBoxQuery(BaseModel):
    """Bounding box query (minLon, minLat, maxLon, maxLat)"""
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)


class PointQuery(BaseModel):
    """Point query with radius"""
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    radius_meters: float = Field(1000, ge=0, le=50000)


class SearchQuery(BaseModel):
    """Text search query"""
    q: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    limit: int = Field(50, ge=1, le=500)
