# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- NGSI-LD Core Components ---

class NGSILDBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')

class Property(NGSILDBase):
    type: Literal["Property"] = "Property"
    value: Any
    observedAt: Optional[datetime] = None
    unitCode: Optional[str] = None
    datasetId: Optional[str] = None

class Relationship(NGSILDBase):
    type: Literal["Relationship"] = "Relationship"
    object: str  # URN of the target entity
    observedAt: Optional[datetime] = None
    datasetId: Optional[str] = None

class GeoProperty(NGSILDBase):
    type: Literal["GeoProperty"] = "GeoProperty"
    value: Dict[str, Any]  # GeoJSON Geometry (Point, Polygon, etc.)

# --- Context Handling ---
# NGSI-LD uses @context to link data to ontologies (SOSA/SSN)
ContextType = Union[str, List[str], Dict[str, Any]]

# --- Main Entity Model ---
class Entity(NGSILDBase):
    id: str = Field(..., description="URN of the entity, e.g., urn:ngsi-ld:Vehicle:A4567")
    type: str = Field(..., description="Entity Type, e.g., Vehicle, AirQualityObserved")
    scope: Optional[Union[str, List[str]]] = None
    location: Optional[GeoProperty] = None
    
    # Dynamic fields (Properties & Relationships) are handled by extra='allow'
    # But we explicitly define context for serialization
    at_context: Optional[ContextType] = Field(None, alias="@context")

    def to_dict(self):
        return self.model_dump(by_alias=True, exclude_none=True)

# --- Common FiWARE Smart Data Models Helpers ---

class AirQualityObserved(Entity):
    """
    Specific model for AirQuality to ensure strict validation if needed.
    Inherits flexibility from Entity but enforces type.
    """
    type: Literal["AirQualityObserved"] = "AirQualityObserved"
    # We can add specific properties here if we want strict schema validation
    # e.g., NO2: Property, CO: Property
    # But usually NGSI-LD is dynamic.

