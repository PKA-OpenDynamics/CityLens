# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Notification endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    DeviceTokenCreate,
    MarkReadRequest,
    NotificationStatsResponse
)

router = APIRouter()


# TODO: Add authentication dependency to get current_user
# For now, using user_id as query parameter (temporary for testing)


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    user_id: int = Query(..., description="User ID (temporary, will use auth)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách thông báo của user
    
    - **user_id**: ID người dùng (sẽ lấy từ JWT token sau)
    - **skip**: Số lượng bỏ qua (phân trang)
    - **limit**: Số lượng tối đa
    - **unread_only**: Chỉ lấy chưa đọc
    """
    service = NotificationService(db)
    
    notifications, total = service.get_user_notifications(
        user_id=user_id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    unread_count = service.get_unread_count(user_id)
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }


@router.get("/count")
async def get_unread_count(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Đếm số thông báo chưa đọc
    
    Endpoint này dùng để hiển thị badge trên app icon/navbar
    """
    service = NotificationService(db)
    count = service.get_unread_count(user_id)
    
    return {"unread_count": count}


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Thống kê thông báo của user"""
    service = NotificationService(db)
    stats = service.get_notification_stats(user_id)
    
    return stats


@router.post("/mark-read")
async def mark_notifications_as_read(
    request: MarkReadRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Đánh dấu thông báo đã đọc
    
    Body:
    ```json
    {
        "notification_ids": [1, 2, 3]
    }
    ```
    """
    service = NotificationService(db)
    count = service.mark_as_read(request.notification_ids, user_id)
    
    return {
        "status": "success",
        "marked": count
    }


@router.post("/mark-all-read")
async def mark_all_as_read(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Đánh dấu tất cả thông báo đã đọc"""
    service = NotificationService(db)
    count = service.mark_all_as_read(user_id)
    
    return {
        "status": "success",
        "marked": count
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Xóa thông báo"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"status": "success"}


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Lấy cài đặt thông báo của user"""
    service = NotificationService(db)
    settings = service.get_user_settings(user_id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )
    
    return settings


@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Cập nhật cài đặt thông báo
    
    Example body:
    ```json
    {
        "enabled_push": true,
        "enabled_email": false,
        "quiet_hours_enabled": true,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "type_settings": {
            "report_status_change": {
                "in_app": true,
                "push": true,
                "email": false
            }
        }
    }
    ```
    """
    service = NotificationService(db)
    settings = service.update_user_settings(
        user_id=user_id,
        settings_data=settings_data.dict(exclude_unset=True)
    )
    
    return settings


@router.post("/device-token")
async def register_device_token(
    token_data: DeviceTokenCreate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Đăng ký device token cho push notifications
    
    Body:
    ```json
    {
        "token": "fcm_token_here",
        "platform": "android"
    }
    ```
    
    Platform: "android" (FCM) or "ios" (APNs)
    """
    service = NotificationService(db)
    success = service.register_device_token(
        user_id=user_id,
        token=token_data.token,
        platform=token_data.platform
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device token"
        )
    
    return {"status": "success"}


@router.delete("/device-token")
async def unregister_device_token(
    token: str = Query(..., description="Device token to remove"),
    platform: str = Query(..., pattern="^(android|ios)$"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Gỡ bỏ device token"""
    service = NotificationService(db)
    success = service.unregister_device_token(
        user_id=user_id,
        token=token,
        platform=platform
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return {"status": "success"}


# Admin endpoints (for testing notification creation)

@router.post("/test/create")
async def create_test_notification(
    user_id: int = Query(...),
    title: str = Query("Test Notification"),
    message: str = Query("This is a test notification"),
    db: Session = Depends(get_db)
):
    """
    Tạo test notification (chỉ dùng cho development)
    
    Endpoint này sẽ bị remove trong production
    """
    from app.models.notification import NotificationType, NotificationChannel
    
    service = NotificationService(db)
    notification = await service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title=title,
        message=message,
        priority=1,
        channels=[NotificationChannel.IN_APP]
    )
    
    return {
        "status": "success",
        "notification_id": notification.id,
        "message": "Test notification created"
    }
