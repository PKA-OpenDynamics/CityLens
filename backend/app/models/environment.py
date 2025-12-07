# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Environmental data models: Air quality, weather, traffic
Layer 2: Semi-dynamic data updated from external APIs
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

from app.db.postgres import Base


class EnvironmentalData(Base):
    """Dữ liệu môi trường: AQI, thời tiết, giao thông"""
    __tablename__ = "environmental_data"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, nullable=True, index=True)
    
    data_type = Column(String(50), nullable=False, index=True,
                      comment="air_quality, weather, noise, traffic")
    
    # Value & unit
    value = Column(DECIMAL(10, 2), comment="Giá trị đo được")
    unit = Column(String(20), comment="Đơn vị: µg/m³, °C, dB, km/h")
    
    # Timestamp
    measured_at = Column(DateTime(timezone=True), nullable=False, index=True,
                        comment="Thời điểm đo")
    
    # Source & additional data
    source = Column(String(50), comment="waqi, openweathermap, google_maps")
    properties = Column(JSONB, comment="Thông tin chi tiết: PM2.5, PM10, humidity, etc.")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
