# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Media models - File storage and management
For reports with images/videos
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.postgres import Base


class MediaFile(Base):
    """Media file storage with metadata"""
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # File info
    file_type = Column(String(20), nullable=False, index=True)  # image, video
    original_filename = Column(String(255))
    file_path = Column(Text, nullable=False)  # Relative: reports/2024/12/uuid.jpg
    file_url = Column(Text, nullable=False)   # Full URL
    thumbnail_url = Column(Text)
    
    # Metadata
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(100))
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Integer)  # For videos, in seconds
    file_metadata = Column(JSONB)  # EXIF, location, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ReportMedia(Base):
    """Many-to-many relationship between reports and media"""
    __tablename__ = "report_media"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    media_id = Column(Integer, ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False, index=True)
    
    display_order = Column(Integer, default=0, nullable=False)
    caption = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserDeviceToken(Base):
    """Device tokens for push notifications (FCM/APNs)"""
    __tablename__ = "user_device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    device_type = Column(String(20), nullable=False)  # ios, android, web
    token = Column(Text, nullable=False, unique=True, index=True)
    device_metadata = Column(JSONB)  # model, os_version, app_version
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))


class SensorObservation(Base):
    """SOSA/SSN compliant sensor observations"""
    __tablename__ = "sensor_observations"

    id = Column(Integer, primary_key=True, index=True)
    
    # SOSA properties
    entity_id = Column(String(255), nullable=False, index=True)  # URN of sensor
    observed_property = Column(String(100), nullable=False, index=True)  # pm25, temperature
    
    result_value = Column(Numeric(10, 2))
    result_unit = Column(String(50))  # μg/m³, °C, %
    result_quality = Column(String(50))  # good, moderate, unhealthy
    
    # Temporal
    phenomenon_time = Column(DateTime(timezone=True), nullable=False, index=True)
    result_time = Column(DateTime(timezone=True))
    
    # Spatial
    from geoalchemy2 import Geometry
    location = Column(Geometry('POINT', srid=4326))
    
    # Metadata
    observation_metadata = Column(JSONB)
    source = Column(String(50), index=True)  # aqicn, openweathermap, tomtom
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
