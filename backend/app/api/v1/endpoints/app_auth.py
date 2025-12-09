# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App Authentication Endpoints
API routes for mobile app user authentication (register, login, profile)
Uses MongoDB Atlas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb_atlas import get_mongodb_atlas
from app.services.app_auth_service import AppAuthService
from app.schemas.app_user import (
    AppUserRegister,
    AppUserLogin,
    AppTokenResponse,
    AppUserProfile,
    AppUserUpdate
)

router = APIRouter()


@router.post("/register", response_model=AppTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: AppUserRegister,
    db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """
    Đăng ký người dùng mới (Mobile App)
    
    - **username**: Tên đăng nhập (unique, 3-50 ký tự)
    - **email**: Email (unique)
    - **password**: Mật khẩu (tối thiểu 6 ký tự)
    - **full_name**: Họ và tên
    - **phone**: Số điện thoại (optional)
    """
    auth_service = AppAuthService(db)
    
    # Validate password length
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu phải có ít nhất 6 ký tự"
        )
    
    # Register user
    user = await auth_service.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    
    # Generate token
    token = auth_service.create_access_token(
        user_id=user.id,
        username=user.username
    )
    
    return AppTokenResponse(
        success=True,
        data={
            "user": user.dict(by_alias=True, exclude={"password"}),
            "access_token": token,
            "token_type": "bearer"
        }
    )


@router.post("/login", response_model=AppTokenResponse)
async def login(
    credentials: AppUserLogin,
    db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """
    Đăng nhập (Mobile App)
    
    - **username**: Tên đăng nhập
    - **password**: Mật khẩu
    """
    auth_service = AppAuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        username=credentials.username,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    
    # Generate token
    token = auth_service.create_access_token(
        user_id=user.id,
        username=user.username
    )
    
    # Remove password from response
    user_dict = user.dict(by_alias=True)
    user_dict.pop("password", None)
    
    return AppTokenResponse(
        success=True,
        data={
            "user": user_dict,
            "access_token": token,
            "token_type": "bearer"
        }
    )


@router.get("/me", response_model=dict)
async def get_profile(
    token: Optional[str] = Query(None, description="Access token (optional if using Authorization header)"),
    authorization: Optional[str] = Header(None, description="Bearer token in Authorization header"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """
    Lấy thông tin profile người dùng hiện tại (Mobile App)
    
    Supports:
    - Bearer token in Authorization header: Authorization: Bearer <token>
    - Token as query parameter: ?token=<token>
    """
    auth_service = AppAuthService(db)
    
    # Get token from header or query param
    access_token = token
    if not access_token and authorization:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            access_token = authorization[7:]
        else:
            access_token = authorization
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không được cung cấp"
        )
    
    # Decode token
    try:
        payload = auth_service.decode_token(access_token)
        user_id = payload.get("userId")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )
        
        # Get user
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        return {
            "success": True,
            "data": user.dict(by_alias=True)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )


@router.put("/me", response_model=dict)
async def update_profile(
    update_data: AppUserUpdate,
    token: Optional[str] = Query(None, description="Access token (optional if using Authorization header)"),
    authorization: Optional[str] = Header(None, description="Bearer token in Authorization header"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """
    Cập nhật thông tin profile (Mobile App)
    
    Supports:
    - Bearer token in Authorization header: Authorization: Bearer <token>
    - Token as query parameter: ?token=<token>
    """
    auth_service = AppAuthService(db)
    
    # Get token from header or query param
    access_token = token
    if not access_token and authorization:
        if authorization.startswith("Bearer "):
            access_token = authorization[7:]
        else:
            access_token = authorization
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không được cung cấp"
        )
    
    # Decode token
    payload = auth_service.decode_token(access_token)
    user_id = payload.get("userId")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )
    
    # Update user
    update_dict = update_data.dict(exclude_unset=True)
    user = await auth_service.update_user_profile(user_id, update_dict)
    
    return {
        "success": True,
        "data": user.dict(by_alias=True)
    }
