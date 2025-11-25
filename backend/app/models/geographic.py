# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Geographic models: Administrative boundaries, streets, buildings
Layer 1: Foundation geographic data from OSM
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry

from app.db.base import Base


class AdministrativeBoundary(Base):
    """Ranh giới hành chính: Thành phố, Quận, Phường"""
    __tablename__ = "administrative_boundaries"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(Integer, unique=True, index=True, comment="OpenStreetMap ID")
    name = Column(String(255), nullable=True, comment="Tên (Tiếng Việt)")  # Some boundaries don't have names
    name_en = Column(String(255), comment="Tên (Tiếng Anh)")
    admin_level = Column(Integer, nullable=False, index=True, comment="4=city, 6=district, 8=ward")
    parent_id = Column(Integer, nullable=True, comment="Parent boundary ID")
    
    # PostGIS geometry
    boundary = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)
    
    # Metadata
    population = Column(Integer, comment="Dân số")
    area_km2 = Column(DECIMAL(10, 2), comment="Diện tích (km²)")
    properties = Column(JSONB, comment="Additional OSM properties")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Street(Base):
    """Đường phố từ OSM"""
    __tablename__ = "streets"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(Integer, unique=True, index=True)
    name = Column(String(255), nullable=True, index=True)  # Some streets don't have names (service roads)
    name_en = Column(String(255))
    street_type = Column(String(50), comment="primary, secondary, residential")
    district_id = Column(Integer, nullable=True, comment="Thuộc quận nào")
    
    # PostGIS geometry
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Metadata
    length_m = Column(DECIMAL(10, 2), comment="Chiều dài (m)")
    surface = Column(String(50), comment="asphalt, concrete")
    lanes = Column(Integer, comment="Số làn xe")
    maxspeed = Column(Integer, comment="Tốc độ tối đa (km/h)")
    properties = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Building(Base):
    """Tòa nhà từ OSM"""
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(Integer, unique=True, index=True)
    name = Column(String(255), index=True)
    building_type = Column(String(50), comment="residential, commercial, office")
    address = Column(String(500))
    district_id = Column(Integer, nullable=True)
    
    # PostGIS geometry
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Metadata
    height_m = Column(DECIMAL(10, 2), comment="Chiều cao (m)")
    levels = Column(Integer, comment="Số tầng")
    properties = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
