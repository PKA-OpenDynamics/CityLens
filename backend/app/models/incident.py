# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Incident models - Sự cố/sự kiện đô thị
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from geoalchemy2 import Geometry
import enum
import uuid
from app.db.postgres import Base


class IncidentType(str, enum.Enum):
    """Loại sự cố"""
    TRAFFIC = "traffic"
    WEATHER = "weather"
    ENVIRONMENTAL = "environmental"
    INFRASTRUCTURE = "infrastructure"
    PUBLIC_SAFETY = "public_safety"
    UTILITY = "utility"


class IncidentSeverity(str, enum.Enum):
    """Mức độ nghiêm trọng"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base):
    """Sự cố/sự kiện đô thị"""
    __tablename__ = "incidents"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Incident info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    type = Column(Enum(IncidentType), nullable=False, index=True)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM, index=True)
    
    # Location
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    address = Column(Text)
    district_id = Column(Integer, nullable=True)
    
    # Time
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Source
    source = Column(String(100), comment="system, user_report, external_api")
    source_id = Column(String(255), comment="ID from source system")
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Impact
    affected_area_radius = Column(Float, comment="Radius in meters")
    estimated_impact = Column(Integer, comment="Number of people affected")
    
    # Additional data
    incident_metadata = Column(JSONB, comment="Extra incident data")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Incident {self.title} ({self.type})>"
