# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Schema cho NGSI-LD entities
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GeoProperty(BaseModel):
    """GeoProperty theo chuẩn NGSI-LD"""
    type: str = "GeoProperty"
    value: Dict[str, Any]


class Property(BaseModel):
    """Property theo chuẩn NGSI-LD"""
    type: str = "Property"
    value: Any
    observedAt: Optional[datetime] = None
    unitCode: Optional[str] = None


class Relationship(BaseModel):
    """Relationship theo chuẩn NGSI-LD"""
    type: str = "Relationship"
    object: str


class NGSILDEntity(BaseModel):
    """Entity chuẩn NGSI-LD"""
    id: str = Field(..., description="URN của entity")
    type: str = Field(..., description="Loại entity")
    context: Optional[List[str]] = Field(
        default=["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
        alias="@context"
    )
    
    class Config:
        populate_by_name = True


class FloodSensor(NGSILDEntity):
    """Sensor ngập nước từ người dân"""
    type: str = "FloodCrowdSensor"
    location: GeoProperty
    waterLevel: Property
    confidence: Property
    reportedBy: Relationship
    observedAt: str


class TrafficSensor(NGSILDEntity):
    """Sensor giao thông từ người dân"""
    type: str = "TrafficCrowdSensor"
    location: GeoProperty
    congestionLevel: Property
    vehicleCount: Optional[Property] = None
    confidence: Property
    reportedBy: Relationship
    observedAt: str


class AQISensor(NGSILDEntity):
    """Sensor chất lượng không khí"""
    type: str = "AirQualityObserved"
    location: GeoProperty
    aqi: Property
    pm25: Optional[Property] = None
    pm10: Optional[Property] = None
    source: Property
    observedAt: str
