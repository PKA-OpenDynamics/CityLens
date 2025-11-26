# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
FiWARE Transportation Domain Models
Spec: https://github.com/smart-data-models/dataModel.Transportation
"""

from pydantic import Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.schemas.ngsi_ld.base import (
    NGSILDEntity,
    NGSILDProperty,
    NGSILDGeoProperty,
    NGSILDRelationship,
)


class TrafficFlowObserved(NGSILDEntity):
    """
    FiWARE Model: TrafficFlowObserved
    
    Represents an observation of traffic flow conditions at a location.
    
    Spec: https://github.com/smart-data-models/dataModel.Transportation/blob/master/TrafficFlowObserved/doc/spec.md
    """
    
    type: str = Field(default="TrafficFlowObserved", const=True)
    
    # Required
    dateObserved: NGSILDProperty = Field(
        ...,
        description="Date and time of observation"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location where traffic was observed"
    )
    
    # Traffic metrics
    intensity: Optional[NGSILDProperty] = Field(
        None,
        description="Total number of vehicles detected during observation period (vehicles/hour)"
    )
    occupancy: Optional[NGSILDProperty] = Field(
        None,
        description="Fraction of observation time where a vehicle has been occupying the lane (0-1)"
    )
    averageVehicleSpeed: Optional[NGSILDProperty] = Field(
        None,
        description="Average speed of vehicles in km/h"
    )
    averageVehicleLength: Optional[NGSILDProperty] = Field(
        None,
        description="Average length of vehicles in meters"
    )
    congested: Optional[NGSILDProperty] = Field(
        None,
        description="Boolean indicating if traffic is congested"
    )
    
    # Vehicle breakdown
    vehicleType: Optional[NGSILDProperty] = Field(
        None,
        description="Type of vehicle: car, bus, truck, motorcycle, bicycle"
    )
    
    # Lane info
    laneId: Optional[NGSILDProperty] = Field(
        None,
        description="Lane identifier"
    )
    laneDirection: Optional[NGSILDProperty] = Field(
        None,
        description="Lane direction: forward, backward"
    )
    
    # References
    refRoadSegment: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to the road segment"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:TrafficFlowObserved:HCM-Street456-2025-11-25T08:00:00Z",
                "type": "TrafficFlowObserved",
                "dateObserved": {
                    "type": "Property",
                    "value": "2025-11-25T08:00:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8542, 21.0285]
                    }
                },
                "intensity": {
                    "type": "Property",
                    "value": 1200,
                    "unitCode": "E50",
                    "description": "vehicles per hour"
                },
                "averageVehicleSpeed": {
                    "type": "Property",
                    "value": 25.5,
                    "unitCode": "KMH"
                },
                "occupancy": {
                    "type": "Property",
                    "value": 0.85
                },
                "congested": {
                    "type": "Property",
                    "value": True
                },
                "refRoadSegment": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:RoadSegment:456"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/master/context.jsonld"
                ]
            }
        }
    )


class RoadAccident(NGSILDEntity):
    """
    FiWARE Model: RoadAccident
    
    Represents a road traffic accident.
    
    Spec: https://github.com/smart-data-models/dataModel.Transportation/blob/master/RoadAccident/doc/spec.md
    """
    
    type: str = Field(default="RoadAccident", const=True)
    
    # Required
    dateObserved: NGSILDProperty = Field(
        ...,
        description="Date and time when accident occurred"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location where accident occurred"
    )
    
    # Accident details
    accidentType: Optional[NGSILDProperty] = Field(
        None,
        description="Type: accident, collision, fall, hit, etc."
    )
    severity: Optional[NGSILDProperty] = Field(
        None,
        description="Severity: mild, serious, fatal"
    )
    status: Optional[NGSILDProperty] = Field(
        None,
        description="Status: onGoing, solved, archived"
    )
    
    # Casualties
    numberOfPeople: Optional[NGSILDProperty] = Field(
        None,
        description="Number of people involved"
    )
    numberOfDeaths: Optional[NGSILDProperty] = Field(
        None,
        description="Number of deaths"
    )
    numberOfInjured: Optional[NGSILDProperty] = Field(
        None,
        description="Number of injured persons"
    )
    
    # Vehicles
    numberOfVehicles: Optional[NGSILDProperty] = Field(
        None,
        description="Number of vehicles involved"
    )
    vehiclesInvolved: Optional[NGSILDProperty] = Field(
        None,
        description="List of vehicle types: car, truck, motorcycle, bicycle"
    )
    
    # Conditions
    weatherConditions: Optional[NGSILDProperty] = Field(
        None,
        description="Weather at time of accident"
    )
    roadConditions: Optional[NGSILDProperty] = Field(
        None,
        description="Road conditions: dry, wet, icy"
    )
    
    # Description
    description: Optional[NGSILDProperty] = Field(
        None,
        description="Accident description"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:RoadAccident:HCM-ACC-20251125-001",
                "type": "RoadAccident",
                "dateObserved": {
                    "type": "Property",
                    "value": "2025-11-25T07:30:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8412, 21.0245]
                    }
                },
                "accidentType": {
                    "type": "Property",
                    "value": "collision"
                },
                "severity": {
                    "type": "Property",
                    "value": "serious"
                },
                "status": {
                    "type": "Property",
                    "value": "onGoing"
                },
                "numberOfPeople": {
                    "type": "Property",
                    "value": 3
                },
                "numberOfInjured": {
                    "type": "Property",
                    "value": 2
                },
                "numberOfVehicles": {
                    "type": "Property",
                    "value": 2
                },
                "vehiclesInvolved": {
                    "type": "Property",
                    "value": ["car", "motorcycle"]
                },
                "description": {
                    "type": "Property",
                    "value": "Collision between car and motorcycle at intersection"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/master/context.jsonld"
                ]
            }
        }
    )

