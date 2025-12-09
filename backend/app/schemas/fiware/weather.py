# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Model: WeatherObserved
https://github.com/smart-data-models/dataModel.Weather/tree/master/WeatherObserved

NGSI-LD compliant weather observation data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class NGSILDProperty(BaseModel):
    """Base NGSI-LD Property"""
    type: str = "Property"
    value: Any
    unitCode: Optional[str] = None
    observedAt: Optional[str] = None


class NGSILDGeoProperty(BaseModel):
    """NGSI-LD GeoProperty"""
    type: str = "GeoProperty"
    value: Dict[str, Any]  # GeoJSON


class WeatherObservedBase(BaseModel):
    """Base schema for WeatherObserved"""
    # Location
    location: Dict[str, Any] = Field(..., description="GeoJSON Point")
    address: Optional[Dict[str, str]] = Field(None, description="Civic address")
    
    # Temperature measurements (Celsius)
    temperature: Optional[float] = Field(None, description="Air temperature")
    feelsLikeTemperature: Optional[float] = Field(None, description="Feels like temperature")
    temperatureMin: Optional[float] = Field(None, description="Minimum temperature")
    temperatureMax: Optional[float] = Field(None, description="Maximum temperature")
    
    # Humidity (%)
    relativeHumidity: Optional[float] = Field(None, ge=0, le=100, description="Relative humidity")
    
    # Pressure (hPa)
    atmosphericPressure: Optional[float] = Field(None, description="Atmospheric pressure")
    pressureTendency: Optional[str] = Field(None, description="Pressure tendency: rising, falling, steady")
    
    # Wind
    windSpeed: Optional[float] = Field(None, ge=0, description="Wind speed in m/s")
    windDirection: Optional[float] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    
    # Precipitation
    precipitation: Optional[float] = Field(None, ge=0, description="Precipitation amount in mm")
    
    # Cloudiness (%)
    cloudCover: Optional[float] = Field(None, ge=0, le=100, description="Cloud coverage")
    
    # Visibility (meters)
    visibility: Optional[float] = Field(None, ge=0, description="Visibility distance")
    
    # Weather description
    weatherType: Optional[str] = Field(None, description="Weather type: clear, cloudy, rainy, etc.")
    description: Optional[str] = Field(None, description="Weather description")
    
    # UV Index
    uvIndex: Optional[float] = Field(None, ge=0, description="UV index")
    
    # Data source
    source: Optional[str] = Field(None, description="Data source URL or identifier")
    dataProvider: Optional[str] = Field(None, description="Provider: OpenWeatherMap, etc.")
    
    # Timestamps
    dateObserved: datetime = Field(..., description="Observation timestamp")


class WeatherObservedCreate(WeatherObservedBase):
    """Schema for creating WeatherObserved"""
    pass


class WeatherObserved(WeatherObservedBase):
    """Full NGSI-LD WeatherObserved entity"""
    id: str = Field(..., description="URN: urn:ngsi-ld:WeatherObserved:{id}")
    type: Literal["WeatherObserved"] = "WeatherObserved"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:ngsi-ld:WeatherObserved:Hanoi:2024-12-09T10:00:00Z",
                "type": "WeatherObserved",
                "location": {
                    "type": "Point",
                    "coordinates": [105.8342, 21.0278]
                },
                "address": {
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                },
                "temperature": 28.5,
                "feelsLikeTemperature": 31.2,
                "relativeHumidity": 75,
                "atmosphericPressure": 1012,
                "windSpeed": 3.5,
                "windDirection": 180,
                "cloudCover": 40,
                "visibility": 10000,
                "weatherType": "partlyCloudy",
                "description": "Partly cloudy",
                "source": "https://api.openweathermap.org",
                "dataProvider": "OpenWeatherMap",
                "dateObserved": "2024-12-09T10:00:00Z"
            }
        }


def to_ngsi_ld_entity(data: WeatherObservedCreate, entity_id: str) -> Dict[str, Any]:
    """
    Convert WeatherObserved to full NGSI-LD entity format
    """
    entity = {
        "id": entity_id,
        "type": "WeatherObserved",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "https://raw.githubusercontent.com/smart-data-models/dataModel.Weather/master/context.jsonld"
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
    
    # Temperature measurements
    if data.temperature is not None:
        entity["temperature"] = {
            "type": "Property",
            "value": data.temperature,
            "unitCode": "CEL",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.feelsLikeTemperature is not None:
        entity["feelsLikeTemperature"] = {
            "type": "Property",
            "value": data.feelsLikeTemperature,
            "unitCode": "CEL",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Humidity
    if data.relativeHumidity is not None:
        entity["relativeHumidity"] = {
            "type": "Property",
            "value": data.relativeHumidity,
            "unitCode": "P1",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Pressure
    if data.atmosphericPressure is not None:
        entity["atmosphericPressure"] = {
            "type": "Property",
            "value": data.atmosphericPressure,
            "unitCode": "A97",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Wind
    if data.windSpeed is not None:
        entity["windSpeed"] = {
            "type": "Property",
            "value": data.windSpeed,
            "unitCode": "MTS",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.windDirection is not None:
        entity["windDirection"] = {
            "type": "Property",
            "value": data.windDirection,
            "unitCode": "DD",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Cloud cover
    if data.cloudCover is not None:
        entity["cloudCover"] = {
            "type": "Property",
            "value": data.cloudCover,
            "unitCode": "P1",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Visibility
    if data.visibility is not None:
        entity["visibility"] = {
            "type": "Property",
            "value": data.visibility,
            "unitCode": "MTR",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Weather type
    if data.weatherType:
        entity["weatherType"] = {
            "type": "Property",
            "value": data.weatherType,
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.description:
        entity["description"] = {
            "type": "Property",
            "value": data.description
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
    
    # Observation time
    entity["dateObserved"] = {
        "type": "Property",
        "value": {
            "@type": "DateTime",
            "@value": data.dateObserved.isoformat() + "Z"
        }
    }
    
    return entity
