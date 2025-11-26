# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
FiWARE Environment Domain Models
Spec: https://github.com/smart-data-models/dataModel.Environment
"""

from pydantic import Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.schemas.ngsi_ld.base import (
    NGSILDEntity,
    NGSILDProperty,
    NGSILDGeoProperty,
    GeoJSONPoint,
)


class AirQualityObserved(NGSILDEntity):
    """
    FiWARE Model: AirQualityObserved
    
    Represents an observation of air quality conditions at a certain place and time.
    
    Spec: https://github.com/smart-data-models/dataModel.Environment/blob/master/AirQualityObserved/doc/spec.md
    """
    
    type: str = Field(default="AirQualityObserved", const=True)
    
    # Required attributes
    dateObserved: NGSILDProperty = Field(
        ...,
        description="Date and time of the observation"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location where the observation was made"
    )
    
    # Address (optional)
    address: Optional[NGSILDProperty] = Field(
        None,
        description="Civic address"
    )
    
    # Pollutants (at least one required)
    PM25: Optional[NGSILDProperty] = Field(
        None,
        description="Particulate Matter 2.5 micrometers or less in diameter (μg/m³)"
    )
    PM10: Optional[NGSILDProperty] = Field(
        None,
        description="Particulate Matter 10 micrometers or less in diameter (μg/m³)"
    )
    NO2: Optional[NGSILDProperty] = Field(
        None,
        description="Nitrogen Dioxide concentration (μg/m³)"
    )
    O3: Optional[NGSILDProperty] = Field(
        None,
        description="Ozone concentration (μg/m³)"
    )
    CO: Optional[NGSILDProperty] = Field(
        None,
        description="Carbon Monoxide concentration (mg/m³)"
    )
    SO2: Optional[NGSILDProperty] = Field(
        None,
        description="Sulfur Dioxide concentration (μg/m³)"
    )
    
    # Air Quality Index
    airQualityIndex: Optional[NGSILDProperty] = Field(
        None,
        description="Overall Air Quality Index"
    )
    airQualityLevel: Optional[NGSILDProperty] = Field(
        None,
        description="Air quality level: good, moderate, unhealthyForSensitiveGroups, unhealthy, veryUnhealthy, hazardous"
    )
    
    # Reliability
    reliability: Optional[NGSILDProperty] = Field(
        None,
        description="Reliability of the measurement (0-1)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:AirQualityObserved:HCM-D1-2025-11-25T10:00:00Z",
                "type": "AirQualityObserved",
                "dateObserved": {
                    "type": "Property",
                    "value": "2025-11-25T10:00:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8345, 21.0368]
                    }
                },
                "address": {
                    "type": "Property",
                    "value": {
                        "addressCountry": "VN",
                        "addressLocality": "Hanoi",
                        "streetAddress": "District 1"
                    }
                },
                "PM25": {
                    "type": "Property",
                    "value": 45.2,
                    "unitCode": "GP",
                    "observedAt": "2025-11-25T10:00:00Z"
                },
                "PM10": {
                    "type": "Property",
                    "value": 78.5,
                    "unitCode": "GP"
                },
                "airQualityIndex": {
                    "type": "Property",
                    "value": 85
                },
                "airQualityLevel": {
                    "type": "Property",
                    "value": "moderate"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
                ]
            }
        }
    )


class WeatherObserved(NGSILDEntity):
    """
    FiWARE Model: WeatherObserved
    
    Represents an observation of weather conditions at a certain place and time.
    
    Spec: https://github.com/smart-data-models/dataModel.Environment/blob/master/WeatherObserved/doc/spec.md
    """
    
    type: str = Field(default="WeatherObserved", const=True)
    
    # Required
    dateObserved: NGSILDProperty = Field(
        ...,
        description="Date of the observed weather"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location where weather was observed"
    )
    
    # Temperature
    temperature: Optional[NGSILDProperty] = Field(
        None,
        description="Air temperature in Celsius"
    )
    feelLikeTemperature: Optional[NGSILDProperty] = Field(
        None,
        description="Feels like temperature in Celsius"
    )
    
    # Humidity
    relativeHumidity: Optional[NGSILDProperty] = Field(
        None,
        description="Relative humidity (0-1)"
    )
    
    # Precipitation
    precipitation: Optional[NGSILDProperty] = Field(
        None,
        description="Precipitation amount in mm"
    )
    
    # Wind
    windSpeed: Optional[NGSILDProperty] = Field(
        None,
        description="Wind speed in m/s"
    )
    windDirection: Optional[NGSILDProperty] = Field(
        None,
        description="Wind direction in degrees (0-360)"
    )
    
    # Pressure
    atmosphericPressure: Optional[NGSILDProperty] = Field(
        None,
        description="Atmospheric pressure in hPa"
    )
    
    # Weather Type
    weatherType: Optional[NGSILDProperty] = Field(
        None,
        description="Weather type: sunny, partlyCloudy, cloudy, rainy, snowy, etc."
    )
    
    # Visibility
    visibility: Optional[NGSILDProperty] = Field(
        None,
        description="Visibility in meters"
    )
    
    # UV Index
    illuminance: Optional[NGSILDProperty] = Field(
        None,
        description="Solar illuminance in lux"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:WeatherObserved:HCM-2025-11-25T10:00:00Z",
                "type": "WeatherObserved",
                "dateObserved": {
                    "type": "Property",
                    "value": "2025-11-25T10:00:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8252, 21.0078]
                    }
                },
                "temperature": {
                    "type": "Property",
                    "value": 32.5,
                    "unitCode": "CEL"
                },
                "relativeHumidity": {
                    "type": "Property",
                    "value": 0.78
                },
                "precipitation": {
                    "type": "Property",
                    "value": 0,
                    "unitCode": "MMT"
                },
                "windSpeed": {
                    "type": "Property",
                    "value": 3.5,
                    "unitCode": "MTS"
                },
                "atmosphericPressure": {
                    "type": "Property",
                    "value": 1013.2,
                    "unitCode": "A97"
                },
                "weatherType": {
                    "type": "Property",
                    "value": "sunny"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
                ]
            }
        }
    )

