# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Model sự kiện thời gian thực
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum
from app.db.postgres import Base


class AlertLevel(str, enum.Enum):
    """Mức độ cảnh báo"""
    INFO = "thong_tin"
    WARNING = "canh_bao"
    DANGER = "nguy_hiem"
    CRITICAL = "khan_cap"


class Incident(Base):
    """Bảng sự kiện được tổng hợp"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Thông tin cơ bản
    incident_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    
    # Mức độ
    alert_level = Column(Enum(AlertLevel), default=AlertLevel.INFO)
    severity_score = Column(Float, default=0.5)
    
    # Vị trí
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    affected_radius = Column(Float, default=500)  # meters
    address = Column(String)
    district = Column(String)
    
    # Nguồn dữ liệu
    source_type = Column(String)  # "citizen", "iot_sensor", "ai_prediction"
    source_ids = Column(String)  # JSON array
    confirmation_count = Column(Integer, default=1)
    
    # Trạng thái
    is_active = Column(Integer, default=1)
    
    # Thời gian
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
