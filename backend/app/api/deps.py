# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API Dependencies
FastAPI dependency injection utilities for PostgreSQL and MongoDB
"""

from typing import Generator, Optional, List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.postgres import SessionLocal
from app.db.mongodb import get_mongodb
from app.services.auth_service import auth_service
from app.services.user_service import UserService
from app.schemas.user import UserRole
from app.core.config import settings

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    PostgreSQL database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== MongoDB User Authentication ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    # Decode token
    token_data = auth_service.decode_token(token)
    
    if not token_data.email or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )
    
    # Get user from MongoDB
    user_service = UserService(db)
    user = await user_service.get_user_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User không tồn tại"
        )
    
    # Validate user status
    auth_service.validate_user_status(user["status"])
    
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency to ensure user is active (approved status)
    """
    if current_user["status"] != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được kích hoạt"
        )
    return current_user


def require_role(required_roles: List[str]):
    """
    Dependency factory to check if user has required role
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role([UserRole.ADMIN]))])
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        auth_service.check_permission(current_user["role"], required_roles)
        return current_user
    
    return role_checker


async def get_current_admin(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Dependency to ensure user is admin or super admin
    """
    if current_user["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền admin"
        )
    return current_user


async def get_current_super_admin(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Dependency to ensure user is super admin
    """
    if current_user["role"] != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ super admin mới có quyền thực hiện"
        )
    return current_user


async def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Dependency for optional authentication (public endpoints with user context)
    Returns user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        token_data = auth_service.decode_token(token)
        
        if not token_data.email or not token_data.user_id:
            return None
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(token_data.user_id)
        
        if not user or user["status"] != "approved":
            return None
        
        return user
        
    except:
        return None

