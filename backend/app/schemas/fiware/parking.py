# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Model: ParkingSpot
https://github.com/smart-data-models/dataModel.Parking/tree/master/ParkingSpot

NGSI-LD compliant parking spot data.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class ParkingSpotBase(BaseModel):
    """Base schema for ParkingSpot"""
    # Location
    location: Dict[str, Any] = Field(..., description="GeoJSON Point or Polygon")
    address: Optional[Dict[str, str]] = Field(None, description="Civic address")
    
    # Spot info
    name: Optional[str] = Field(None, description="Parking spot name")
    category: Optional[str] = Field(None, description="Category: offStreet, onStreet, etc.")
    
    # Status
    status: str = Field(..., description="Status: free, occupied, closed, unknown")
    
    # Vehicle type
    allowedVehicleType: Optional[str] = Field(None, description="Allowed: car, motorcycle, bicycle, etc.")
    
    # Relationships
    refParkingSite: Optional[str] = Field(None, description="Reference to parent parking site")
    
    # Timestamps
    dateModified: datetime = Field(..., description="Last modification timestamp")


class ParkingSpotCreate(ParkingSpotBase):
    """Schema for creating ParkingSpot"""
    pass


class ParkingSpot(ParkingSpotBase):
    """Full NGSI-LD ParkingSpot entity"""
    id: str = Field(..., description="URN: urn:ngsi-ld:ParkingSpot:{id}")
    type: Literal["ParkingSpot"] = "ParkingSpot"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:ngsi-ld:ParkingSpot:Hanoi-TimesCity-A-001",
                "type": "ParkingSpot",
                "location": {
                    "type": "Point",
                    "coordinates": [105.8342, 21.0278]
                },
                "name": "Spot A-001",
                "category": "offStreet",
                "status": "free",
                "allowedVehicleType": "car",
                "refParkingSite": "urn:ngsi-ld:ParkingSite:Hanoi-TimesCity",
                "dateModified": "2024-12-09T10:00:00Z"
            }
        }


def to_ngsi_ld_entity(data: ParkingSpotCreate, entity_id: str) -> Dict[str, Any]:
    """
    Convert ParkingSpot to full NGSI-LD entity format
    """
    entity = {
        "id": entity_id,
        "type": "ParkingSpot",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"
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
    
    # Name
    if data.name:
        entity["name"] = {
            "type": "Property",
            "value": data.name
        }
    
    # Category
    if data.category:
        entity["category"] = {
            "type": "Property",
            "value": data.category
        }
    
    # Status
    entity["status"] = {
        "type": "Property",
        "value": data.status,
        "observedAt": data.dateModified.isoformat() + "Z"
    }
    
    # Vehicle type
    if data.allowedVehicleType:
        entity["allowedVehicleType"] = {
            "type": "Property",
            "value": data.allowedVehicleType
        }
    
    # Relationship
    if data.refParkingSite:
        entity["refParkingSite"] = {
            "type": "Relationship",
            "object": data.refParkingSite
        }
    
    # Timestamps
    entity["dateModified"] = {
        "type": "Property",
        "value": {
            "@type": "DateTime",
            "@value": data.dateModified.isoformat() + "Z"
        }
    }
    
    return entity
