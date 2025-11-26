# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
NGSI-LD Base Schema Definitions
Implements ETSI GS CIM 009 V1.6.1 standard
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum


class NGSILDType(str, Enum):
    """NGSI-LD attribute types"""
    PROPERTY = "Property"
    GEO_PROPERTY = "GeoProperty"
    RELATIONSHIP = "Relationship"
    TEMPORAL_PROPERTY = "TemporalProperty"


class NGSILDProperty(BaseModel):
    """
    NGSI-LD Property
    
    A Property is a piece of information describing an Entity.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = Field(default="Property", const=True)
    value: Any = Field(..., description="The actual value of the property")
    observedAt: Optional[datetime] = Field(
        None,
        description="Timestamp when the property was observed"
    )
    unitCode: Optional[str] = Field(
        None,
        description="Unit of measurement (UN/CEFACT Common Code)",
        examples=["CEL", "LUX", "GP"]
    )
    datasetId: Optional[str] = Field(
        None,
        description="Identifier of the dataset this property belongs to"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "Property",
                "value": 45.2,
                "observedAt": "2025-11-25T10:30:00Z",
                "unitCode": "GP"
            }
        }
    )


class GeoJSONPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: str = Field(default="Point", const=True)
    coordinates: List[float] = Field(
        ...,
        description="[longitude, latitude] or [longitude, latitude, altitude]",
        min_length=2,
        max_length=3
    )
    
    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) < 2:
            raise ValueError("Point must have at least longitude and latitude")
        # Validate longitude [-180, 180]
        if not -180 <= v[0] <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {v[0]}")
        # Validate latitude [-90, 90]
        if not -90 <= v[1] <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {v[1]}")
        return v


class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon geometry"""
    type: str = Field(default="Polygon", const=True)
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="Array of linear ring coordinate arrays"
    )


class GeoJSONLineString(BaseModel):
    """GeoJSON LineString geometry"""
    type: str = Field(default="LineString", const=True)
    coordinates: List[List[float]] = Field(
        ...,
        description="Array of positions"
    )


GeoJSONGeometry = Union[GeoJSONPoint, GeoJSONPolygon, GeoJSONLineString]


class NGSILDGeoProperty(BaseModel):
    """
    NGSI-LD GeoProperty
    
    A GeoProperty is a specialized Property that represents a geographic location.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = Field(default="GeoProperty", const=True)
    value: GeoJSONGeometry = Field(
        ...,
        description="GeoJSON geometry object"
    )
    observedAt: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [105.8542, 21.0285]
                }
            }
        }
    )


class NGSILDRelationship(BaseModel):
    """
    NGSI-LD Relationship
    
    A Relationship represents a link between entities.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = Field(default="Relationship", const=True)
    object: str = Field(
        ...,
        description="URI of the target entity",
        pattern=r"^urn:ngsi-ld:[\w]+:[\w\-:]+$"
    )
    observedAt: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:District:1"
            }
        }
    )


class NGSILDContext(BaseModel):
    """NGSI-LD @context"""
    contexts: List[str] = Field(
        default=[
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ],
        alias="@context"
    )
    
    model_config = ConfigDict(populate_by_name=True)


class NGSILDEntity(BaseModel):
    """
    NGSI-LD Entity (Base Class)
    
    An Entity represents something that exists in the real world.
    All domain-specific entities should inherit from this class.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra='allow'  # Allow additional fields for domain-specific properties
    )
    
    id: str = Field(
        ...,
        description="Unique identifier (URI)",
        pattern=r"^urn:ngsi-ld:[\w]+:[\w\-:]+$",
        examples=["urn:ngsi-ld:AirQualityObserved:HCM-D1-001"]
    )
    type: str = Field(
        ...,
        description="Entity type",
        examples=["AirQualityObserved", "TrafficFlowObserved", "CitizenReport"]
    )
    context: Union[List[str], str] = Field(
        default=[
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ],
        alias="@context",
        description="JSON-LD context"
    )
    
    # Common optional attributes
    createdAt: Optional[datetime] = Field(
        None,
        description="Entity creation timestamp (system-managed)"
    )
    modifiedAt: Optional[datetime] = Field(
        None,
        description="Entity modification timestamp (system-managed)"
    )
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Validate NGSI-LD ID format"""
        if not v.startswith('urn:ngsi-ld:'):
            raise ValueError(f"ID must start with 'urn:ngsi-ld:', got: {v}")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:Example:001",
                "type": "ExampleEntity",
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
            }
        }
    )
    
    def to_rdf(self) -> str:
        """
        Convert entity to RDF Turtle format
        For storage in GraphDB
        """
        # This will be implemented in GraphDB service
        pass


class NGSILDEntityFragment(BaseModel):
    """
    NGSI-LD Entity Fragment
    Used for partial updates (PATCH operations)
    """
    model_config = ConfigDict(
        populate_by_name=True,
        extra='allow'
    )
    
    # Only attributes to be updated
    attributes: Dict[str, Union[NGSILDProperty, NGSILDGeoProperty, NGSILDRelationship]]


class NGSILDEntityList(BaseModel):
    """Response model for entity lists"""
    entities: List[NGSILDEntity] = Field(default_factory=list)
    count: Optional[int] = None
    next: Optional[str] = Field(None, description="Link to next page")
    prev: Optional[str] = Field(None, description="Link to previous page")

