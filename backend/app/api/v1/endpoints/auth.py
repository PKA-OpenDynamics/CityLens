# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Authentication API Endpoints
User registration, login, profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta

from app.db.mongodb import get_mongodb
from app.api.deps import get_current_user, get_current_active_user
from app.services.auth_service import auth_service
from app.services.user_service import UserService
from app.schemas.user import (
    UserRegister, UserLogin, UserUpdate, PasswordChange,
    RegisterResponse, LoginResponse, UserBase, UserProfile,
    Token, MessageResponse
)
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db = Depends(get_mongodb)
):
    """
    Đăng ký tài khoản mới cho web-dashboard
    
    - **email**: Email đăng nhập (@citylens.com hoặc email cơ quan nhà nước)
    - **password**: Mật khẩu (tối thiểu 8 ký tự, có chữ và số)
    - **full_name**: Họ và tên đầy đủ
    - **phone**: Số điện thoại liên hệ
    - **department**: Phòng ban (Sở GTVT, Sở XD, UBND, ...)
    - **position**: Chức vụ (Chuyên viên, Phó giám đốc, ...)
    - **reason**: Lý do cần sử dụng hệ thống
    
    Sau khi đăng ký, tài khoản sẽ ở trạng thái **PENDING** và cần admin duyệt.
    """
    user_service = UserService(db)
    
    # Create user
    new_user = await user_service.create_user(user_data)
    
    # Remove password from response
    new_user.pop("hashed_password", None)
    
    return {
        "user": new_user,
        "message": "Đăng ký thành công. Tài khoản đang chờ duyệt từ admin."
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    db = Depends(get_mongodb)
):
    """
    Đăng nhập vào web-dashboard
    
    - **email**: Email đã đăng ký
    - **password**: Mật khẩu
    
    Trả về access token và refresh token để sử dụng cho các request sau.
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )
    
    # Create tokens
    token_data = {
        "sub": user["email"],
        "user_id": user["_id"],
        "role": user["role"]
    }
    
    access_token = auth_service.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = auth_service.create_refresh_token(data=token_data)
    
    # Remove password from response
    user.pop("hashed_password", None)
    
    return {
        "user": user,
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        },
        "message": "Đăng nhập thành công"
    }


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lấy thông tin profile của user đang đăng nhập
    """
    # Remove password from response
    current_user.pop("hashed_password", None)
    
    return UserProfile(**current_user)


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db = Depends(get_mongodb)
):
    """
    Cập nhật thông tin profile của user đang đăng nhập
    
    - **full_name**: Họ và tên
    - **phone**: Số điện thoại
    - **department**: Phòng ban
    - **position**: Chức vụ
    - **avatar_url**: URL ảnh đại diện
    """
    user_service = UserService(db)
    
    updated_user = await user_service.update_user_profile(
        current_user["_id"],
        update_data
    )
    
    # Remove password from response
    updated_user.pop("hashed_password", None)
    
    return UserProfile(**updated_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user),
    db = Depends(get_mongodb)
):
    """
    Đổi mật khẩu
    
    - **old_password**: Mật khẩu cũ
    - **new_password**: Mật khẩu mới (tối thiểu 8 ký tự, có chữ và số)
    """
    user_service = UserService(db)
    
    await user_service.change_password(
        current_user["_id"],
        password_data.old_password,
        password_data.new_password
    )
    
    return MessageResponse(
        message="Đổi mật khẩu thành công"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db = Depends(get_mongodb)
):
    """
    Làm mới access token bằng refresh token
    
    - **refresh_token**: Refresh token nhận được khi đăng nhập
    """
    # Decode refresh token
    try:
        token_data = auth_service.decode_token(refresh_token)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ"
        )
    
    # Verify user still exists and is active
    user_service = UserService(db)
    user = await user_service.get_user_by_id(token_data.user_id)
    
    if not user or user["status"] != "approved":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User không hợp lệ"
        )
    
    # Create new tokens
    new_token_data = {
        "sub": user["email"],
        "user_id": user["_id"],
        "role": user["role"]
    }
    
    new_access_token = auth_service.create_access_token(
        data=new_token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    new_refresh_token = auth_service.create_refresh_token(data=new_token_data)
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
