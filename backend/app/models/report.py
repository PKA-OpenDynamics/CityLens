# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Report models - Báo cáo từ người dân
Layer 3: Citizen generated data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
import enum
from app.db.postgres import Base


class ReportStatus(str, enum.Enum):
    """Trạng thái báo cáo"""
    PENDING = "pending"  # Chờ xử lý
    VERIFIED = "verified"  # Đã xác minh
    IN_PROGRESS = "in_progress"  # Đang xử lý
    RESOLVED = "resolved"  # Đã giải quyết
    REJECTED = "rejected"  # Từ chối
    DUPLICATE = "duplicate"  # Trùng lặp


class ReportPriority(str, enum.Enum):
    """Mức độ ưu tiên"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReportCategory(Base):
    """Danh mục báo cáo"""
    __tablename__ = "report_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_vi = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(7))
    parent_id = Column(Integer, ForeignKey("report_categories.id"), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    """Báo cáo từ người dân - Core table"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Category
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(50))
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Location
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    address = Column(String(500))
    district_id = Column(Integer, nullable=True, index=True)
    
    # Links to Layer 2 (optional)
    related_facility_id = Column(Integer, nullable=True)
    related_street_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)
    priority = Column(Enum(ReportPriority), default=ReportPriority.NORMAL, nullable=False)
    
    # Images (array of URLs)
    images = Column(ARRAY(Text), default=[])
    
    # Report metadata (renamed to avoid conflict with SQLAlchemy Base.metadata)
    report_metadata = Column(JSONB)
    
    # Engagement metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Verification
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True))
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True))
    resolution_note = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportComment(Base):
    """Bình luận trên báo cáo"""
    __tablename__ = "report_comments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("report_comments.id"), nullable=True)
    
    content = Column(Text, nullable=False)
    images = Column(ARRAY(Text), default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportVote(Base):
    """Vote trên báo cáo"""
    __tablename__ = "report_votes"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vote_type = Column(String(10), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportFollower(Base):
    """Theo dõi báo cáo"""
    __tablename__ = "report_followers"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportActivity(Base):
    """Lịch sử thay đổi báo cáo"""
    __tablename__ = "report_activities"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(50), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
