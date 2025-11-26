# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
FiWARE Urban Infrastructure Domain Models
Spec: https://github.com/smart-data-models/dataModel.UrbanMobility
"""

from pydantic import Field, ConfigDict
from typing import Optional

from app.schemas.ngsi_ld.base import (
    NGSILDEntity,
    NGSILDProperty,
    NGSILDGeoProperty,
    NGSILDRelationship,
)


class StreetLight(NGSILDEntity):
    """
    FiWARE Model: Streetlight
    
    Represents a street light.
    
    Spec: https://github.com/smart-data-models/dataModel.Streetlighting/blob/master/Streetlight/doc/spec.md
    """
    
    type: str = Field(default="Streetlight", const=True)
    
    # Required
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location of the streetlight"
    )
    status: NGSILDProperty = Field(
        ...,
        description="Status: ok, defectiveLamp, columnIssue, brokenLantern"
    )
    powerState: NGSILDProperty = Field(
        ...,
        description="Power state: on, off, low, bootingUp"
    )
    
    # Circuit
    circuit: Optional[NGSILDProperty] = Field(
        None,
        description="Circuit identifier"
    )
    
    # Physical specs
    lanternHeight: Optional[NGSILDProperty] = Field(
        None,
        description="Lantern height in meters"
    )
    lampType: Optional[NGSILDProperty] = Field(
        None,
        description="Lamp type: LED, LPS, HPS, MH, etc."
    )
    lampPower: Optional[NGSILDProperty] = Field(
        None,
        description="Lamp power in Watts"
    )
    
    # Measurements
    illuminanceLevel: Optional[NGSILDProperty] = Field(
        None,
        description="Illuminance level in lux"
    )
    powerConsumption: Optional[NGSILDProperty] = Field(
        None,
        description="Power consumption in Watts"
    )
    
    # Control
    controllingMethod: Optional[NGSILDProperty] = Field(
        None,
        description="Method: individual, group, SCADA"
    )
    
    # References
    refStreetlightGroup: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to streetlight group"
    )
    refStreetlightControlCabinet: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to control cabinet"
    )
    refRoad: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to road segment"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:Streetlight:HCM-Street456-Light-001",
                "type": "Streetlight",
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8542, 21.0285]
                    }
                },
                "status": {
                    "type": "Property",
                    "value": "ok"
                },
                "powerState": {
                    "type": "Property",
                    "value": "on",
                    "observedAt": "2025-11-25T18:00:00Z"
                },
                "lampType": {
                    "type": "Property",
                    "value": "LED"
                },
                "lampPower": {
                    "type": "Property",
                    "value": 50,
                    "unitCode": "WTT"
                },
                "illuminanceLevel": {
                    "type": "Property",
                    "value": 120,
                    "unitCode": "LUX"
                },
                "powerConsumption": {
                    "type": "Property",
                    "value": 48,
                    "unitCode": "WTT"
                },
                "refRoad": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Road:456"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Streetlighting/master/context.jsonld"
                ]
            }
        }
    )


class WaterQualityObserved(NGSILDEntity):
    """
    FiWARE Model: WaterQualityObserved
    
    Represents an observation of water quality.
    
    Spec: https://github.com/smart-data-models/dataModel.Environment/blob/master/WaterQualityObserved/doc/spec.md
    """
    
    type: str = Field(default="WaterQualityObserved", const=True)
    
    # Required
    dateObserved: NGSILDProperty = Field(
        ...,
        description="Date of observation"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location where water quality was observed"
    )
    
    # Physical parameters
    temperature: Optional[NGSILDProperty] = Field(
        None,
        description="Water temperature in Celsius"
    )
    pH: Optional[NGSILDProperty] = Field(
        None,
        description="pH level (0-14)"
    )
    conductivity: Optional[NGSILDProperty] = Field(
        None,
        description="Electrical conductivity in μS/cm"
    )
    turbidity: Optional[NGSILDProperty] = Field(
        None,
        description="Turbidity in NTU (Nephelometric Turbidity Units)"
    )
    
    # Chemical parameters
    dissolvedOxygen: Optional[NGSILDProperty] = Field(
        None,
        description="Dissolved oxygen in mg/L"
    )
    BOD: Optional[NGSILDProperty] = Field(
        None,
        description="Biochemical Oxygen Demand in mg/L"
    )
    COD: Optional[NGSILDProperty] = Field(
        None,
        description="Chemical Oxygen Demand in mg/L"
    )
    
    # Pollutants
    NH4: Optional[NGSILDProperty] = Field(
        None,
        description="Ammonium concentration in mg/L"
    )
    NO3: Optional[NGSILDProperty] = Field(
        None,
        description="Nitrate concentration in mg/L"
    )
    
    # Source
    measurand: Optional[NGSILDProperty] = Field(
        None,
        description="Array of observed properties"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:WaterQualityObserved:HCM-River-001",
                "type": "WaterQualityObserved",
                "dateObserved": {
                    "type": "Property",
                    "value": "2025-11-25T10:00:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8412, 21.0245]
                    }
                },
                "temperature": {
                    "type": "Property",
                    "value": 28.5,
                    "unitCode": "CEL"
                },
                "pH": {
                    "type": "Property",
                    "value": 7.2
                },
                "conductivity": {
                    "type": "Property",
                    "value": 450,
                    "unitCode": "G42"
                },
                "turbidity": {
                    "type": "Property",
                    "value": 15.3,
                    "unitCode": "NTU"
                },
                "dissolvedOxygen": {
                    "type": "Property",
                    "value": 6.8,
                    "unitCode": "M1"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
                ]
            }
        }
    )

