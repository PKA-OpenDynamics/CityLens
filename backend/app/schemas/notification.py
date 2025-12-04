# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Notification schemas
"""

from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.notification import NotificationType, NotificationChannel


class NotificationBase(BaseModel):
    """Schema cơ bản cho Notification"""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=3)


class NotificationCreate(NotificationBase):
    """Schema tạo Notification mới"""
    user_id: int
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]


class NotificationResponse(NotificationBase):
    """Schema trả về Notification"""
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    sent_in_app: bool
    sent_push: bool
    sent_email: bool
    sent_sms: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema cho danh sách Notification"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationSettingsBase(BaseModel):
    """Schema cơ bản cho User Notification Settings"""
    enabled_in_app: bool = True
    enabled_push: bool = True
    enabled_email: bool = True
    enabled_sms: bool = False
    type_settings: Optional[Dict[str, Dict[str, bool]]] = None
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class NotificationSettingsUpdate(NotificationSettingsBase):
    """Schema cập nhật Notification Settings"""
    pass


class NotificationSettingsResponse(NotificationSettingsBase):
    """Schema trả về Notification Settings"""
    id: int
    user_id: int
    fcm_tokens: List[str] = []
    apns_tokens: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceTokenCreate(BaseModel):
    """Schema đăng ký device token"""
    token: str = Field(..., min_length=1)
    platform: str = Field(..., pattern="^(android|ios)$")  # android or ios


class MarkReadRequest(BaseModel):
    """Schema đánh dấu đã đọc"""
    notification_ids: List[int]


class NotificationStatsResponse(BaseModel):
    """Schema thống kê thông báo"""
    total: int
    unread: int
    by_type: Dict[str, int]
    last_7_days: int
