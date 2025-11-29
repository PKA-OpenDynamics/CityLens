# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Schema cho Report API
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.report import IncidentType, ReportStatus


class ReportBase(BaseModel):
    """Schema cơ bản cho Report"""
    incident_type: IncidentType
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    severity: int = Field(default=3, ge=1, le=5)
    address: Optional[str] = None
    district: Optional[str] = None


class ReportCreate(ReportBase):
    """Schema tạo Report mới"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    incident_time: datetime
    media_urls: Optional[List[str]] = None


class ReportUpdate(BaseModel):
    """Schema cập nhật Report"""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=5)


class ReportInDB(ReportBase):
    """Schema Report trong database"""
    id: int
    user_id: int
    latitude: float
    longitude: float
    status: ReportStatus
    confidence_score: float
    verification_count: int
    incident_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportResponse(ReportInDB):
    """Schema response Report cho API"""
    user_username: Optional[str] = None
    distance: Optional[float] = None  # Khoảng cách đến người dùng (km)


class ReportVerify(BaseModel):
    """Schema xác thực báo cáo (admin)"""
    status: ReportStatus
    admin_note: Optional[str] = None


class ReportStats(BaseModel):
    """Thống kê báo cáo"""
    total: int
    pending: int
    verified: int
    rejected: int
    resolved: int
    by_type: dict
    by_district: dict
