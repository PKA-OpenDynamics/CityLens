# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Model: TrafficFlowObserved
https://github.com/smart-data-models/dataModel.Transportation/tree/master/TrafficFlowObserved

NGSI-LD compliant traffic flow observation data.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class TrafficFlowObservedBase(BaseModel):
    """Base schema for TrafficFlowObserved"""
    # Location
    location: Dict[str, Any] = Field(..., description="GeoJSON Point or LineString")
    address: Optional[Dict[str, str]] = Field(None, description="Civic address")
    
    # Road segment
    roadSegment: Optional[str] = Field(None, description="Road segment identifier")
    laneId: Optional[int] = Field(None, description="Lane number")
    laneDirection: Optional[str] = Field(None, description="Direction: forward, backward")
    
    # Traffic metrics
    intensity: Optional[float] = Field(None, ge=0, description="Vehicle count per hour")
    occupancy: Optional[float] = Field(None, ge=0, le=1, description="Lane occupancy ratio")
    averageVehicleSpeed: Optional[float] = Field(None, ge=0, description="Average speed km/h")
    averageVehicleLength: Optional[float] = Field(None, ge=0, description="Average vehicle length in meters")
    
    # Congestion
    congested: Optional[bool] = Field(None, description="Is traffic congested")
    congestionLevel: Optional[str] = Field(None, description="Level: low, medium, high, critical")
    
    # Vehicle types
    vehicleType: Optional[str] = Field(None, description="Predominant vehicle type")
    vehicleSubType: Optional[str] = Field(None, description="Vehicle subtype")
    
    # Data source
    source: Optional[str] = Field(None, description="Data source URL")
    dataProvider: Optional[str] = Field(None, description="Provider: TomTom, Google, etc.")
    
    # Timestamps
    dateObserved: datetime = Field(..., description="Observation timestamp")
    dateObservedFrom: Optional[datetime] = Field(None, description="Observation period start")
    dateObservedTo: Optional[datetime] = Field(None, description="Observation period end")


class TrafficFlowObservedCreate(TrafficFlowObservedBase):
    """Schema for creating TrafficFlowObserved"""
    pass


class TrafficFlowObserved(TrafficFlowObservedBase):
    """Full NGSI-LD TrafficFlowObserved entity"""
    id: str = Field(..., description="URN: urn:ngsi-ld:TrafficFlowObserved:{id}")
    type: Literal["TrafficFlowObserved"] = "TrafficFlowObserved"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:ngsi-ld:TrafficFlowObserved:Hanoi-GiaiPhong-001",
                "type": "TrafficFlowObserved",
                "location": {
                    "type": "LineString",
                    "coordinates": [[105.8342, 21.0278], [105.8352, 21.0288]]
                },
                "address": {
                    "streetAddress": "Giải Phóng Street",
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                },
                "roadSegment": "GiaiPhong-Segment-1",
                "laneId": 1,
                "laneDirection": "forward",
                "intensity": 1250,
                "occupancy": 0.75,
                "averageVehicleSpeed": 25.5,
                "congested": True,
                "congestionLevel": "high",
                "vehicleType": "car",
                "source": "https://api.tomtom.com",
                "dataProvider": "TomTom",
                "dateObserved": "2024-12-09T10:00:00Z"
            }
        }


def to_ngsi_ld_entity(data: TrafficFlowObservedCreate, entity_id: str) -> Dict[str, Any]:
    """
    Convert TrafficFlowObserved to full NGSI-LD entity format
    """
    entity = {
        "id": entity_id,
        "type": "TrafficFlowObserved",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/master/context.jsonld"
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
    
    # Road segment
    if data.roadSegment:
        entity["roadSegment"] = {
            "type": "Property",
            "value": data.roadSegment
        }
    
    if data.laneId is not None:
        entity["laneId"] = {
            "type": "Property",
            "value": data.laneId
        }
    
    if data.laneDirection:
        entity["laneDirection"] = {
            "type": "Property",
            "value": data.laneDirection
        }
    
    # Traffic metrics
    if data.intensity is not None:
        entity["intensity"] = {
            "type": "Property",
            "value": data.intensity,
            "unitCode": "E34",  # vehicles per hour
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.occupancy is not None:
        entity["occupancy"] = {
            "type": "Property",
            "value": data.occupancy,
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.averageVehicleSpeed is not None:
        entity["averageVehicleSpeed"] = {
            "type": "Property",
            "value": data.averageVehicleSpeed,
            "unitCode": "KMH",
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Congestion
    if data.congested is not None:
        entity["congested"] = {
            "type": "Property",
            "value": data.congested,
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    if data.congestionLevel:
        entity["congestionLevel"] = {
            "type": "Property",
            "value": data.congestionLevel,
            "observedAt": data.dateObserved.isoformat() + "Z"
        }
    
    # Vehicle type
    if data.vehicleType:
        entity["vehicleType"] = {
            "type": "Property",
            "value": data.vehicleType
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
    
    if data.dateObservedFrom:
        entity["dateObservedFrom"] = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": data.dateObservedFrom.isoformat() + "Z"
            }
        }
    
    if data.dateObservedTo:
        entity["dateObservedTo"] = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": data.dateObservedTo.isoformat() + "Z"
            }
        }
    
    return entity
