# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
NGSI-LD Query Parameters
For filtering and querying entities
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class GeoRelation(str, Enum):
    """Geospatial relationships"""
    NEAR = "near"
    WITHIN = "within"
    CONTAINS = "contains"
    OVERLAPS = "overlaps"
    INTERSECTS = "intersects"
    EQUALS = "equals"
    DISJOINT = "disjoint"


class GeometryType(str, Enum):
    """GeoJSON geometry types"""
    POINT = "Point"
    POLYGON = "Polygon"
    LINESTRING = "LineString"
    MULTIPOINT = "MultiPoint"
    MULTIPOLYGON = "MultiPolygon"
    MULTILINESTRING = "MultiLineString"


class NGSILDGeoQuery(BaseModel):
    """
    NGSI-LD Geo-Query parameters
    
    Example:
        georel=near;maxDistance==5000
        geometry=Point
        coordinates=[106.6927,10.7769]
    """
    georel: str = Field(
        ...,
        description="Geospatial relationship with optional parameters",
        examples=["near;maxDistance==5000", "within", "intersects"]
    )
    geometry: GeometryType = Field(
        ...,
        description="Geometry type"
    )
    coordinates: str = Field(
        ...,
        description="Coordinates as string (format depends on geometry)",
        examples=["[106.6927,10.7769]", "[[106.6,10.7],[106.7,10.8]]"]
    )
    geoproperty: str = Field(
        default="location",
        description="Name of the GeoProperty to query against"
    )
    
    def parse_georel(self) -> tuple[GeoRelation, dict]:
        """
        Parse georel parameter
        
        Returns:
            (relation, params) tuple
            
        Example:
            "near;maxDistance==5000" -> (GeoRelation.NEAR, {"maxDistance": 5000})
        """
        parts = self.georel.split(";")
        relation = GeoRelation(parts[0])
        params = {}
        
        for part in parts[1:]:
            if "==" in part:
                key, value = part.split("==")
                # Try to convert to number
                try:
                    params[key] = float(value)
                except ValueError:
                    params[key] = value
        
        return relation, params
    
    def parse_coordinates(self) -> list:
        """
        Parse coordinates string to list
        
        Returns:
            Coordinates as Python list
        """
        import json
        return json.loads(self.coordinates)


class NGSILDQuery(BaseModel):
    """
    NGSI-LD Query Parameters
    
    Used for filtering entities in GET /entities endpoint
    """
    
    # Entity Type
    type: Optional[str] = Field(
        None,
        description="Entity type filter (comma-separated for multiple)",
        examples=["AirQualityObserved", "TrafficFlowObserved,CitizenReport"]
    )
    
    # ID Pattern
    id: Optional[str] = Field(
        None,
        description="Entity ID or pattern",
        examples=["urn:ngsi-ld:AirQualityObserved:HCM-D1-001"]
    )
    idPattern: Optional[str] = Field(
        None,
        description="Regular expression for ID matching",
        examples=["urn:ngsi-ld:AirQualityObserved:HCM-D.*"]
    )
    
    # Attributes
    attrs: Optional[str] = Field(
        None,
        description="Comma-separated list of attributes to include",
        examples=["location,dateObserved,airQualityIndex"]
    )
    
    # Query Language (NGSI-LD Q filter)
    q: Optional[str] = Field(
        None,
        description="Query filter using NGSI-LD query language",
        examples=[
            "temperature>25",
            "category=='infrastructure'",
            "status=='pending';priority=='high'"
        ]
    )
    
    # Geo-Query
    georel: Optional[str] = Field(
        None,
        description="Geospatial relationship",
        examples=["near;maxDistance==5000"]
    )
    geometry: Optional[GeometryType] = Field(
        None,
        description="Geometry type for geo-query"
    )
    coordinates: Optional[str] = Field(
        None,
        description="Coordinates for geo-query"
    )
    geoproperty: str = Field(
        default="location",
        description="GeoProperty to query against"
    )
    
    # Pagination
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination"
    )
    
    # Temporal Query (optional, for future)
    timerel: Optional[str] = Field(
        None,
        description="Temporal relationship",
        examples=["after", "before", "between"]
    )
    timeAt: Optional[str] = Field(
        None,
        description="Time instant for temporal query"
    )
    
    # Options
    options: Optional[str] = Field(
        None,
        description="Query options (comma-separated)",
        examples=["keyValues", "sysAttrs"]
    )
    
    def get_type_list(self) -> List[str]:
        """Parse type parameter into list"""
        if not self.type:
            return []
        return [t.strip() for t in self.type.split(",")]
    
    def get_attrs_list(self) -> List[str]:
        """Parse attrs parameter into list"""
        if not self.attrs:
            return []
        return [a.strip() for a in self.attrs.split(",")]
    
    def has_geo_query(self) -> bool:
        """Check if this is a geo-query"""
        return all([self.georel, self.geometry, self.coordinates])
    
    def get_geo_query(self) -> Optional[NGSILDGeoQuery]:
        """Get geo-query parameters as object"""
        if not self.has_geo_query():
            return None
        
        return NGSILDGeoQuery(
            georel=self.georel,
            geometry=self.geometry,
            coordinates=self.coordinates,
            geoproperty=self.geoproperty
        )
    
    def parse_q_filter(self) -> List[dict]:
        """
        Parse Q filter into structured format
        
        Example:
            "temperature>25;status=='active'" ->
            [
                {"attribute": "temperature", "op": ">", "value": 25},
                {"attribute": "status", "op": "==", "value": "active"}
            ]
        """
        if not self.q:
            return []
        
        filters = []
        conditions = self.q.split(";")
        
        for condition in conditions:
            for op in ["==", "!=", ">=", "<=", ">", "<", "~="]:
                if op in condition:
                    attr, value = condition.split(op, 1)
                    attr = attr.strip()
                    value = value.strip().strip("'\"")
                    
                    # Try to convert to number
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    
                    filters.append({
                        "attribute": attr,
                        "operator": op,
                        "value": value
                    })
                    break
        
        return filters


class NGSILDBatchOperation(BaseModel):
    """
    NGSI-LD Batch Operation
    For creating/updating/deleting multiple entities at once
    """
    entities: List[dict] = Field(
        ...,
        description="List of entities to process"
    )


class NGSILDSubscription(BaseModel):
    """
    NGSI-LD Subscription (for future)
    Allows clients to subscribe to entity changes
    """
    id: Optional[str] = None
    type: str = "Subscription"
    entities: List[dict] = Field(
        ...,
        description="Entity patterns to watch"
    )
    watchedAttributes: Optional[List[str]] = None
    notification: dict = Field(
        ...,
        description="Notification configuration"
    )

