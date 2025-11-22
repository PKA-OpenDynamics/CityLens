# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Model báo cáo từ người dân
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum
from app.db.postgres import Base


class IncidentType(str, enum.Enum):
    """Loại sự cố"""
    FLOOD = "ngap_nuoc"
    TRAFFIC_JAM = "ket_xe"
    POOR_AQI = "aqi_kem"
    ACCIDENT = "tai_nan"
    ROAD_DAMAGE = "duong_hong"
    HIGH_TIDE = "trieu_cuong"
    OTHER = "khac"


class ReportStatus(str, enum.Enum):
    """Trạng thái báo cáo"""
    PENDING = "cho_xac_nhan"
    VERIFIED = "da_xac_nhan"
    REJECTED = "tu_choi"
    RESOLVED = "da_giai_quyet"


class Report(Base):
    """Bảng báo cáo sự cố"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Thông tin sự cố
    incident_type = Column(Enum(IncidentType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(Integer, default=3)  # 1-5
    
    # Vị trí
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    address = Column(String)
    district = Column(String)
    city = Column(String, default="Thành phố Hồ Chí Minh")
    
    # Metadata
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    confidence_score = Column(Float, default=0.5)
    verification_count = Column(Integer, default=0)
    
    # Media
    media_urls = Column(String)  # JSON array as string
    
    # Thời gian
    incident_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
