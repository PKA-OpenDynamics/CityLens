# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
FiWARE Parking Domain Models
Spec: https://github.com/smart-data-models/dataModel.Parking
"""

from pydantic import Field, ConfigDict
from typing import Optional, List

from app.schemas.ngsi_ld.base import (
    NGSILDEntity,
    NGSILDProperty,
    NGSILDGeoProperty,
    NGSILDRelationship,
)


class OffStreetParking(NGSILDEntity):
    """
    FiWARE Model: OffStreetParking
    
    Represents an off-street parking facility (parking lot or garage).
    
    Spec: https://github.com/smart-data-models/dataModel.Parking/blob/master/OffStreetParking/doc/spec.md
    """
    
    type: str = Field(default="OffStreetParking", const=True)
    
    # Required
    name: NGSILDProperty = Field(
        ...,
        description="Name of the parking facility"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location of parking facility"
    )
    
    # Capacity
    totalSpotNumber: NGSILDProperty = Field(
        ...,
        description="Total number of parking spots"
    )
    availableSpotNumber: NGSILDProperty = Field(
        ...,
        description="Number of currently available spots"
    )
    occupancy: Optional[NGSILDProperty] = Field(
        None,
        description="Occupancy rate (0-1)"
    )
    occupancyDetectionType: Optional[NGSILDProperty] = Field(
        None,
        description="Type: none, balancing, singleSpaceDetection, modelBased"
    )
    
    # Address
    address: Optional[NGSILDProperty] = Field(
        None,
        description="Civic address"
    )
    
    # Category
    category: Optional[NGSILDProperty] = Field(
        None,
        description="Categories: public, private, publicPrivate, etc."
    )
    
    # Parking modes
    allowedVehicleType: Optional[NGSILDProperty] = Field(
        None,
        description="Vehicle types: car, motorcycle, bicycle, bus"
    )
    parkingMode: Optional[NGSILDProperty] = Field(
        None,
        description="Modes: perpendicularParking, parallelParking, echelonParking"
    )
    
    # Facilities
    facilities: Optional[NGSILDProperty] = Field(
        None,
        description="Facilities: CCTV, lighting, toilet, paymentTerminal, etc."
    )
    security: Optional[NGSILDProperty] = Field(
        None,
        description="Security features"
    )
    
    # Pricing
    priceRate: Optional[NGSILDProperty] = Field(
        None,
        description="Price per hour"
    )
    priceCurrency: Optional[NGSILDProperty] = Field(
        None,
        description="Currency code (ISO 4217)"
    )
    
    # Operating hours
    openingHours: Optional[NGSILDProperty] = Field(
        None,
        description="Opening hours in schema.org format"
    )
    
    # Status
    status: Optional[NGSILDProperty] = Field(
        None,
        description="Status: open, closed, full, almostFull"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:OffStreetParking:HCM-BenThanh",
                "type": "OffStreetParking",
                "name": {
                    "type": "Property",
                    "value": "Bãi xe Bến Thành"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8345, 21.0368]
                    }
                },
                "totalSpotNumber": {
                    "type": "Property",
                    "value": 200
                },
                "availableSpotNumber": {
                    "type": "Property",
                    "value": 45,
                    "observedAt": "2025-11-25T10:30:00Z"
                },
                "occupancy": {
                    "type": "Property",
                    "value": 0.775
                },
                "category": {
                    "type": "Property",
                    "value": ["public"]
                },
                "allowedVehicleType": {
                    "type": "Property",
                    "value": ["car", "motorcycle"]
                },
                "priceRate": {
                    "type": "Property",
                    "value": 15000,
                    "unitCode": "VND"
                },
                "priceCurrency": {
                    "type": "Property",
                    "value": "VND"
                },
                "status": {
                    "type": "Property",
                    "value": "open"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"
                ]
            }
        }
    )


class ParkingSpot(NGSILDEntity):
    """
    FiWARE Model: ParkingSpot
    
    Represents an individual parking spot.
    """
    
    type: str = Field(default="ParkingSpot", const=True)
    
    # Required
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location of the spot"
    )
    status: NGSILDProperty = Field(
        ...,
        description="Status: free, occupied, reserved, closed"
    )
    
    # Spot details
    name: Optional[NGSILDProperty] = Field(
        None,
        description="Spot identifier (e.g., A-12)"
    )
    category: Optional[NGSILDProperty] = Field(
        None,
        description="Categories: onstreet, offstreet"
    )
    
    # Vehicle type
    allowedVehicleType: Optional[NGSILDProperty] = Field(
        None,
        description="Allowed vehicle type"
    )
    
    # Special spots
    specialSpot: Optional[NGSILDProperty] = Field(
        None,
        description="Special features: disabled, electric, etc."
    )
    
    # Reference to parking facility
    refParkingFacility: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to parent parking facility"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:ParkingSpot:HCM-BenThanh-A12",
                "type": "ParkingSpot",
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [105.8345, 21.0368]
                    }
                },
                "status": {
                    "type": "Property",
                    "value": "free",
                    "observedAt": "2025-11-25T10:30:00Z"
                },
                "name": {
                    "type": "Property",
                    "value": "A-12"
                },
                "allowedVehicleType": {
                    "type": "Property",
                    "value": "car"
                },
                "refParkingFacility": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:OffStreetParking:HCM-BenThanh"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
            }
        }
    )

