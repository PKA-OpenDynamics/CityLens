# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App Report Schema
Compatible with web-app/server Report model
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class MediaItem(BaseModel):
    """Media attachment (image or video)"""
    uri: str  # URL or base64
    type: str  # 'image' or 'video'
    filename: Optional[str] = None


class LocationData(BaseModel):
    """GPS coordinates"""
    lat: float
    lng: float


class AppReportCreate(BaseModel):
    """Mobile app report creation request"""
    reportType: str  # Loại phản ánh
    ward: str  # Xã/phường
    addressDetail: Optional[str] = ""  # Số nhà, thôn/xóm, khu vực
    location: Optional[LocationData] = None
    title: Optional[str] = ""  # Tiêu đề
    content: str  # Nội dung phản ánh
    media: List[MediaItem] = []
    userId: Optional[str] = None  # ID người dùng


class AppReport(BaseModel):
    """Mobile app report (matches web-app/server model)"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    reportType: str
    ward: str
    addressDetail: str = ""
    location: Optional[LocationData] = None
    title: str = ""
    content: str
    media: List[MediaItem] = []
    userId: Optional[str] = None
    status: str = "pending"  # pending, processing, resolved, rejected
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AppReportResponse(BaseModel):
    """API response for report"""
    success: bool = True
    data: dict


class AppReportListResponse(BaseModel):
    """API response for report list"""
    success: bool = True
    data: List[dict]
    count: int


class AppReportUpdate(BaseModel):
    """Update report (admin only)"""
    status: Optional[str] = None  # pending, processing, resolved, rejected
    adminNote: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    reportType: Optional[str] = None
    ward: Optional[str] = None
    addressDetail: Optional[str] = None


# Comment Schemas
class AppCommentCreate(BaseModel):
    """Create a new comment"""
    content: str  # Nội dung bình luận
    userId: Optional[str] = None  # ID người dùng
    userName: Optional[str] = None  # Tên người dùng


class AppCommentResponse(BaseModel):
    """API response for comment"""
    success: bool = True
    data: dict


class AppCommentListResponse(BaseModel):
    """API response for comment list"""
    success: bool = True
    data: List[dict]
    count: int