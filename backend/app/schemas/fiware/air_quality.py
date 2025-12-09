# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Model: AirQualityObserved
https://github.com/smart-data-models/dataModel.Environment/tree/master/AirQualityObserved

NGSI-LD compliant air quality observation data.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class AirQualityObservedBase(BaseModel):
    """Base schema for AirQualityObserved"""
    # Location
    location: Dict[str, Any] = Field(..., description="GeoJSON Point")
    address: Optional[Dict[str, str]] = Field(None, description="Civic address")
    
    # Air Quality Index
    airQualityIndex: float = Field(..., description="Overall AQI value")
    airQualityLevel: Optional[str] = Field(None, description="Level: good, moderate, unhealthy, etc.")
    
    # Pollutants (μg/m³)
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 concentration")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 concentration")
    no2: Optional[float] = Field(None, ge=0, description="NO2 concentration")
    so2: Optional[float] = Field(None, ge=0, description="SO2 concentration")
    co: Optional[float] = Field(None, ge=0, description="CO concentration")
    o3: Optional[float] = Field(None, ge=0, description="O3 (Ozone) concentration")
    
    # Station info
    stationName: Optional[str] = Field(None, description="Monitoring station name")
    stationCode: Optional[str] = Field(None, description="Station identifier")
    
    # Data source
    source: Optional[str] = Field(None, description="Data source URL")
    dataProvider: Optional[str] = Field(None, description="Provider: AQICN, WAQI, etc.")
    
    # Health information
    healthRecommendations: Optional[str] = Field(None, description="Health advice")
    
    # Reliability
    reliability: Optional[float] = Field(None, ge=0, le=1, description="Data reliability score")
    
    # Timestamps
    dateObserved: datetime = Field(..., description="Observation timestamp")


class AirQualityObservedCreate(AirQualityObservedBase):
    """Schema for creating AirQualityObserved"""
    pass


class AirQualityObserved(AirQualityObservedBase):
    """Full NGSI-LD AirQualityObserved entity"""
    id: str = Field(..., description="URN: urn:ngsi-ld:AirQualityObserved:{id}")
    type: Literal["AirQualityObserved"] = "AirQualityObserved"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:ngsi-ld:AirQualityObserved:Hanoi:2024-12-09T10:00:00Z",
                "type": "AirQualityObserved",
                "location": {
                    "type": "Point",
                    "coordinates": [105.8342, 21.0278]
                },
                "address": {
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                },
                "airQualityIndex": 155,
                "airQualityLevel": "unhealthy",
                "pm25": 65.3,
                "pm10": 98.5,
                "no2": 45.2,
                "so2": 12.8,
                "co": 850,
                "o3": 32.1,
                "stationName": "Hanoi US Embassy",
                "stationCode": "H13026",
                "source": "https://api.waqi.info",
                "dataProvider": "AQICN",
                "healthRecommendations": "Sensitive groups should reduce outdoor activity",
                "dateObserved": "2024-12-09T10:00:00Z"
            }
        }


def to_ngsi_ld_entity(data: AirQualityObservedCreate, entity_id: str) -> Dict[str, Any]:
    """
    Convert AirQualityObserved to full NGSI-LD entity format
    """
    entity = {
        "id": entity_id,
        "type": "AirQualityObserved",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
        ]
    }
    
    # Location (GeoProperty)
    entity["location"] = {
        "type": "GeoProperty",
        "value": data.location
    }
    
    # Address
    if data.address:
        entity["address"] = {
            "type": "Property",
            "value": data.address
        }
    
    # AQI
    entity["airQualityIndex"] = {
        "type": "Property",
        "value": data.airQualityIndex,
        "observedAt": data.dateObserved.isoformat() + "Z"
    }
    
    if data.airQualityLevel:
        entity["airQualityLevel"] = {
            "type": "Property",
            "value": data.airQualityLevel,
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Pollutants
    if data.pm25 is not None:
        entity["pm25"] = {
            "type": "Property",
            "value": data.pm25,
            "unitCode": "GQ",  # μg/m³
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.pm10 is not None:
        entity["pm10"] = {
            "type": "Property",
            "value": data.pm10,
            "unitCode": "GQ",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.no2 is not None:
        entity["no2"] = {
            "type": "Property",
            "value": data.no2,
            "unitCode": "GQ",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.so2 is not None:
        entity["so2"] = {
            "type": "Property",
            "value": data.so2,
            "unitCode": "GQ",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.co is not None:
        entity["co"] = {
            "type": "Property",
            "value": data.co,
            "unitCode": "GQ",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.o3 is not None:
        entity["o3"] = {
            "type": "Property",
            "value": data.o3,
            "unitCode": "GQ",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Station info
    if data.stationName:
        entity["stationName"] = {
            "type": "Property",
            "value": data.stationName
        }
    
    if data.stationCode:
        entity["stationCode"] = {
            "type": "Property",
            "value": data.stationCode
        }
    
    # Data provenance
    if data.source:
        entity["source"] = {
            "type": "Property",
            "value": data.source
        }
    
    if data.dataProvider:
        entity["dataProvider"] = {
            "type": "Property",
            "value": data.dataProvider
        }
    
    # Health recommendations
    if data.healthRecommendations:
        entity["healthRecommendations"] = {
            "type": "Property",
            "value": data.healthRecommendations
        }
    
    # Reliability
    if data.reliability is not None:
        entity["reliability"] = {
            "type": "Property",
            "value": data.reliability
        }
    
    # Observation time
    entity["dateObserved"] = {
        "type": "Property",
        "value": {
            "@type": "DateTime",
            "@value": data.dateObserved.isoformat() + "Z"
        }
    }
    
    return entity
