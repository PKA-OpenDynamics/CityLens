# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
SQLAlchemy models for OSM Administrative Areas and Facilities
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class AdministrativeArea(Base):
    """
    Administrative boundaries (City, Districts, Wards)
    Corresponds to admin_level 4, 6, 8 in OSM
    """
    __tablename__ = "administrative_areas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    osm_id = Column(BigInteger, nullable=False, unique=True, index=True)
    osm_type = Column(String(20), nullable=False)  # 'node', 'way', 'relation'
    admin_level = Column(Integer, nullable=False, index=True)  # 4, 6, 8
    name = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255))
    name_vi = Column(String(255))
    boundary_type = Column(String(50))  # 'administrative'
    parent_id = Column(Integer, ForeignKey('administrative_areas.id'), nullable=True, index=True)
    population = Column(Integer)
    area_km2 = Column(Float)
    tags = Column(JSONB)  # All OSM tags
    
    # PostGIS geometry columns
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=4326))  # Full boundary
    center_point = Column(Geometry(geometry_type='POINT', srid=4326))  # Center for quick queries
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("AdministrativeArea", remote_side=[id], backref="children")
    facilities = relationship("Facility", back_populates="admin_area")
    
    def __repr__(self):
        return f"<AdministrativeArea(id={self.id}, name='{self.name}', level={self.admin_level})>"
    
    @property
    def level_name(self):
        """Human-readable admin level name"""
        level_names = {4: "City", 6: "District", 8: "Ward"}
        return level_names.get(self.admin_level, f"Level {self.admin_level}")


class Facility(Base):
    """
    Points of Interest / Facilities (hospitals, schools, parks, etc.)
    """
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    osm_id = Column(BigInteger, nullable=False, index=True)
    osm_type = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # 'healthcare', 'education', etc.
    amenity = Column(String(100), nullable=False, index=True)  # 'hospital', 'school', etc.
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    name_vi = Column(String(255))
    
    # Address fields
    address_street = Column(String(255))
    address_district = Column(String(100))
    address_city = Column(String(100))
    
    # Contact info
    phone = Column(String(50))
    website = Column(String(255))
    opening_hours = Column(String(255))
    
    # Foreign key to administrative area
    admin_area_id = Column(Integer, ForeignKey('administrative_areas.id'), nullable=True, index=True)
    
    # All OSM tags
    tags = Column(JSONB)
    
    # PostGIS location (always a point)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    admin_area = relationship("AdministrativeArea", back_populates="facilities")
    
    def __repr__(self):
        return f"<Facility(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    @property
    def full_address(self):
        """Construct full address string"""
        parts = [p for p in [self.address_street, self.address_district, self.address_city] if p]
        return ", ".join(parts) if parts else None
