# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Schema cho User API
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Schema cơ bản cho User"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema tạo User mới"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema cập nhật User"""
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserInDB(UserBase):
    """Schema User trong database"""
    id: int
    level: int
    points: int
    reputation_score: float
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema response User cho API"""
    pass


class UserStats(BaseModel):
    """Thống kê người dùng"""
    total_reports: int
    verified_reports: int
    accuracy_rate: float
    total_points: int
    current_level: int
    rank_in_district: Optional[int] = None
    rank_in_city: Optional[int] = None


class Token(BaseModel):
    """Schema JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload trong JWT token"""
    sub: Optional[int] = None
