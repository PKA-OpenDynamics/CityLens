# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User model - Người dùng hệ thống
Layer 3: Citizen accounts
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from geoalchemy2 import Geometry
import enum
import uuid
from app.db.postgres import Base


class UserRole(str, enum.Enum):
    """Vai trò người dùng"""
    CITIZEN = "citizen"  # Người dân
    MODERATOR = "moderator"  # Kiểm duyệt viên
    ADMIN = "admin"  # Quản trị viên
    GOVERNMENT = "government"  # Cán bộ chính quyền


class User(Base):
    """Bảng người dùng"""
    __tablename__ = "users"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False, index=True)
    
    # Gamification
    level = Column(Integer, default=1)
    points = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.5)
    
    # Trạng thái
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False, comment="Email verified")
    is_admin = Column(Boolean, default=False)
    
    # Location (optional) - link to ward (admin_level=6)
    ward_id = Column(Integer, nullable=True, comment="Phường/xã cư trú")
    location = Column(Geometry('POINT', srid=4326), nullable=True)
    
    # Statistics
    reports_count = Column(Integer, default=0)
    
    # Metadata
    avatar_url = Column(String(500))
    bio = Column(String(500))
    properties = Column(JSONB)
    
    # Thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
