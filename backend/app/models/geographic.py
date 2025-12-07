# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Geographic models - OSM data (Layer 1: Geographic Foundation)
Administrative boundaries, roads, buildings from OpenStreetMap
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, Float, DateTime, Boolean, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from app.db.postgres import Base


class AdministrativeBoundary(Base):
    """
    Ranh giới hành chính từ OSM
    admin_level: 4=province, 5=district, 6=ward, 7=hamlet
    """
    __tablename__ = "administrative_boundaries"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True, nullable=False)
    osm_type = Column(String(10), nullable=False, comment="node, way, relation")
    
    # Administrative info
    name = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255))
    admin_level = Column(Integer, nullable=False, index=True)
    
    # Hierarchy
    parent_id = Column(Integer, nullable=True, comment="Parent admin boundary")
    
    # Geometry - Polygon or MultiPolygon (nullable for relations that need post-processing)
    geometry = Column(Geometry('GEOMETRY', srid=4326), nullable=True)
    
    # Additional OSM tags
    tags = Column(JSONB, comment="All OSM tags as JSON")
    
    # Population data (if available)
    population = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AdminBoundary {self.name} (level {self.admin_level})>"


class Street(Base):
    """
    Đường phố từ OSM
    """
    __tablename__ = "streets"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True, nullable=False)
    osm_type = Column(String(10), nullable=False)
    
    # Street info
    name = Column(String(255), index=True)
    name_en = Column(String(255))
    highway_type = Column(String(50), nullable=False, index=True,
                          comment="primary, secondary, residential, footway, etc.")
    
    # Surface & status
    surface = Column(String(50), comment="asphalt, concrete, unpaved")
    lanes = Column(Integer)
    maxspeed = Column(Integer, comment="km/h")
    oneway = Column(Boolean, default=False)
    
    # District reference
    district_id = Column(Integer, nullable=True)
    
    # Geometry - LineString
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Length in meters
    length = Column(Float, comment="Length in meters")
    
    # OSM tags
    tags = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Street {self.name or 'unnamed'} ({self.highway_type})>"


class Building(Base):
    """
    Tòa nhà từ OSM
    """
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True, nullable=False)
    osm_type = Column(String(10), nullable=False)
    
    # Building info
    name = Column(String(255), index=True)
    building_type = Column(String(50), index=True,
                           comment="residential, commercial, school, hospital, etc.")
    
    # Address
    addr_street = Column(String(255))
    addr_housenumber = Column(String(50))
    addr_district = Column(String(100))
    
    # Building attributes
    levels = Column(Integer, comment="Number of floors")
    height = Column(Float, comment="Height in meters")
    
    # District reference
    district_id = Column(Integer, nullable=True)
    
    # Geometry - Polygon
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Area in square meters
    area = Column(Float, comment="Area in square meters")
    
    # OSM tags
    tags = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Building {self.name or 'unnamed'} ({self.building_type})>"


class POI(Base):
    """
    Points of Interest từ OSM - các địa điểm quan trọng
    """
    __tablename__ = "pois"
    
    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(BigInteger, unique=True, index=True, nullable=False)
    osm_type = Column(String(10), nullable=False)
    
    # POI info
    name = Column(String(255), index=True)
    name_en = Column(String(255))
    
    # Category
    category = Column(String(50), nullable=False, index=True,
                      comment="amenity, shop, tourism, leisure, etc.")
    subcategory = Column(String(50), index=True,
                         comment="restaurant, hospital, atm, hotel, etc.")
    
    # Contact
    phone = Column(String(50))
    website = Column(String(255))
    email = Column(String(255))
    
    # Address
    address = Column(Text)
    
    # District reference
    district_id = Column(Integer, nullable=True)
    
    # Geometry - Point
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # OSM tags
    tags = Column(JSONB)
    
    # Opening hours
    opening_hours = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<POI {self.name or 'unnamed'} ({self.category}/{self.subcategory})>"
