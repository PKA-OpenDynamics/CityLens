# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User Schemas for Dashboard Authentication & Authorization
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


# ==================== User Roles & Status ====================

class UserRole(str):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"  # Có thể duyệt tất cả user
    ADMIN = "admin"               # Quản lý toàn bộ thành phố
    MANAGER = "manager"           # Quản lý khu vực/chức năng cụ thể
    ANALYST = "analyst"           # Phân tích dữ liệu, xem báo cáo
    VIEWER = "viewer"             # Chỉ xem, không chỉnh sửa


class UserStatus(str):
    """User account status"""
    PENDING = "pending"           # Đang chờ duyệt
    APPROVED = "approved"         # Đã được duyệt, hoạt động
    REJECTED = "rejected"         # Bị từ chối
    SUSPENDED = "suspended"       # Bị tạm ngưng
    INACTIVE = "inactive"         # Không hoạt động


# ==================== Request Schemas ====================

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., min_length=8, description="Mật khẩu (tối thiểu 8 ký tự)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    department: Optional[str] = Field(None, description="Phòng ban")
    position: Optional[str] = Field(None, description="Chức vụ")
    reason: Optional[str] = Field(None, description="Lý do đăng ký sử dụng hệ thống")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        if not any(c.isdigit() for c in v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
        if not any(c.isalpha() for c in v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ cái')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="Email đăng nhập")
    password: str = Field(..., description="Mật khẩu")


class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str = Field(..., description="Mật khẩu cũ")
    new_password: str = Field(..., min_length=8, description="Mật khẩu mới")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        if not any(c.isdigit() for c in v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
        if not any(c.isalpha() for c in v):
            raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ cái')
        return v


class UserApproval(BaseModel):
    """Admin approval request"""
    status: Literal["approved", "rejected"] = Field(..., description="Quyết định duyệt")
    role: Optional[Literal["admin", "manager", "analyst", "viewer"]] = Field(
        default="viewer",
        description="Vai trò được gán (nếu approved)"
    )
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối (nếu rejected)")


# ==================== Response Schemas ====================

class UserBase(BaseModel):
    """User base information"""
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    
    id: str = Field(alias="_id", description="User ID")
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = Field(default=UserRole.VIEWER)
    status: str = Field(default=UserStatus.PENDING)
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserProfile(UserBase):
    """Full user profile (for authenticated user)"""
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class UserInDB(UserProfile):
    """User document in MongoDB (includes password hash)"""
    hashed_password: str


class UserPublic(UserBase):
    """Public user information (for admin listing)"""
    reason: Optional[str] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")


class TokenData(BaseModel):
    """JWT token payload"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


class LoginResponse(BaseModel):
    """Login success response"""
    user: UserBase
    token: Token
    message: str = "Đăng nhập thành công"


class RegisterResponse(BaseModel):
    """Registration success response"""
    user: UserBase
    message: str = "Đăng ký thành công. Tài khoản đang chờ duyệt từ admin."


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


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
