# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Admin API Endpoints
User management, approval, role assignment
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.db.mongodb import get_mongodb
from app.api.deps import get_current_admin, get_current_super_admin, get_current_active_user
from app.services.user_service import UserService
from app.schemas.user import (
    UserPublic, UserProfile, UserApproval,
    MessageResponse, UserStatus, UserRole
)

router = APIRouter()


@router.get("/users/pending", response_model=List[UserPublic])
async def get_pending_users(
    skip: int = Query(0, ge=0, description="Số user bỏ qua"),
    limit: int = Query(50, ge=1, le=100, description="Số user tối đa trả về"),
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Lấy danh sách user đang chờ duyệt
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    user_service = UserService(db)
    
    pending_users = await user_service.get_pending_users(skip=skip, limit=limit)
    
    # Remove passwords
    for user in pending_users:
        user.pop("hashed_password", None)
    
    return [UserPublic(**user) for user in pending_users]


@router.get("/users", response_model=List[UserPublic])
async def get_all_users(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: pending, approved, rejected, suspended"),
    role: Optional[str] = Query(None, description="Lọc theo vai trò: admin, manager, analyst, viewer"),
    skip: int = Query(0, ge=0, description="Số user bỏ qua"),
    limit: int = Query(50, ge=1, le=100, description="Số user tối đa trả về"),
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Lấy danh sách tất cả user với filter
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    user_service = UserService(db)
    
    users = await user_service.get_all_users(
        status=status,
        role=role,
        skip=skip,
        limit=limit
    )
    
    # Remove passwords
    for user in users:
        user.pop("hashed_password", None)
    
    return [UserPublic(**user) for user in users]


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Lấy thông tin chi tiết của một user
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Remove password
    user.pop("hashed_password", None)
    
    return UserProfile(**user)


@router.put("/users/{user_id}/approve", response_model=UserProfile)
async def approve_user(
    user_id: str,
    approval_data: UserApproval,
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Duyệt hoặc từ chối đăng ký user
    
    **Yêu cầu**: Admin hoặc Super Admin
    
    - **status**: "approved" (duyệt) hoặc "rejected" (từ chối)
    - **role**: Vai trò gán cho user nếu duyệt (admin, manager, analyst, viewer)
    - **rejection_reason**: Lý do từ chối (nếu rejected)
    """
    user_service = UserService(db)
    
    # Check if trying to approve as super_admin
    if approval_data.status == "approved" and approval_data.role == "super_admin":
        # Only super_admin can create other super_admins
        if current_user["role"] != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ super admin mới có thể tạo super admin khác"
            )
    
    updated_user = await user_service.approve_user(
        user_id,
        approval_data,
        current_user["_id"]
    )
    
    # Remove password
    updated_user.pop("hashed_password", None)
    
    return UserProfile(**updated_user)


@router.put("/users/{user_id}/role", response_model=UserProfile)
async def update_user_role(
    user_id: str,
    new_role: str = Query(..., description="Vai trò mới: admin, manager, analyst, viewer"),
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Thay đổi vai trò của user
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    # Validate role
    valid_roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST, UserRole.VIEWER]
    
    if new_role == UserRole.SUPER_ADMIN:
        # Only super_admin can assign super_admin role
        if current_user["role"] != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ super admin mới có thể gán quyền super admin"
            )
        valid_roles.append(UserRole.SUPER_ADMIN)
    
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vai trò không hợp lệ. Chọn từ: {', '.join(valid_roles)}"
        )
    
    user_service = UserService(db)
    
    updated_user = await user_service.update_user_role(
        user_id,
        new_role,
        current_user["_id"]
    )
    
    # Remove password
    updated_user.pop("hashed_password", None)
    
    return UserProfile(**updated_user)


@router.post("/users/{user_id}/suspend", response_model=MessageResponse)
async def suspend_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Tạm ngưng tài khoản user
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    # Cannot suspend yourself
    if user_id == current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạm ngưng tài khoản của chính mình"
        )
    
    user_service = UserService(db)
    
    # Check target user
    target_user = await user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Only super_admin can suspend admin
    if target_user["role"] == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không thể tạm ngưng tài khoản super admin"
        )
    
    if target_user["role"] == UserRole.ADMIN and current_user["role"] != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ super admin mới có thể tạm ngưng admin"
        )
    
    await user_service.suspend_user(user_id, current_user["_id"])
    
    return MessageResponse(
        message="Đã tạm ngưng tài khoản user"
    )


@router.get("/stats", response_model=dict)
async def get_user_stats(
    current_user: dict = Depends(get_current_admin),
    db = Depends(get_mongodb)
):
    """
    Lấy thống kê về user
    
    **Yêu cầu**: Admin hoặc Super Admin
    """
    user_service = UserService(db)
    
    total_users = await user_service.count_users()
    pending_users = await user_service.count_users(status=UserStatus.PENDING)
    approved_users = await user_service.count_users(status=UserStatus.APPROVED)
    rejected_users = await user_service.count_users(status=UserStatus.REJECTED)
    suspended_users = await user_service.count_users(status=UserStatus.SUSPENDED)
    
    return {
        "total": total_users,
        "pending": pending_users,
        "approved": approved_users,
        "rejected": rejected_users,
        "suspended": suspended_users
    }
