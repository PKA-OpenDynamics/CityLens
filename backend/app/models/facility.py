# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Facility models: Public facilities, transportation infrastructure
Layer 2: Urban infrastructure data (hospitals, schools, bus stops)
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry

from app.db.postgres import Base


class PublicFacility(Base):
    """Cơ sở công cộng: Bệnh viện, trường học, công viên"""
    __tablename__ = "public_facilities"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(Integer, unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False, index=True)
    name_en = Column(String(255))
    
    category = Column(String(50), nullable=False, index=True, 
                     comment="hospital, school, park, police_station, fire_station, library, market")
    subcategory = Column(String(50), comment="Chi tiết: primary_school, general_hospital")
    
    address = Column(String(500))
    district_id = Column(Integer, nullable=True)
    
    # PostGIS geometry - Point location
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Contact & metadata
    phone = Column(String(20))
    website = Column(String(255))
    opening_hours = Column(String(255))
    capacity = Column(Integer, comment="Sức chứa")
    rating = Column(DECIMAL(2, 1), comment="Đánh giá 0-5")
    
    properties = Column(JSONB)
    source = Column(String(50), default='osm', comment="osm, gov, manual")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransportFacility(Base):
    """Cơ sở giao thông: Trạm xe buýt, metro, taxi"""
    __tablename__ = "transport_facilities"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(Integer, unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    
    facility_type = Column(String(50), nullable=False, index=True,
                          comment="bus_stop, metro_station, taxi_stand, parking")
    line_number = Column(String(20), comment="Số tuyến xe buýt/metro")
    
    district_id = Column(Integer, nullable=True)
    
    # PostGIS geometry
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    properties = Column(JSONB)
    source = Column(String(50), default='osm')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
