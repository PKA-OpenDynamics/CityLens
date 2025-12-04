# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Notification models - Hệ thống thông báo cho người dùng
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.db.postgres import Base


class NotificationType(str, enum.Enum):
    """Loại thông báo"""
    REPORT_STATUS_CHANGE = "report_status_change"  # Báo cáo thay đổi trạng thái
    REPORT_COMMENT = "report_comment"  # Có comment mới trên báo cáo
    REPORT_ASSIGNED = "report_assigned"  # Báo cáo được phân công
    REPORT_RESOLVED = "report_resolved"  # Báo cáo được giải quyết
    REPORT_VERIFIED = "report_verified"  # Báo cáo được xác minh
    REPORT_REJECTED = "report_rejected"  # Báo cáo bị từ chối
    COMMENT_REPLY = "comment_reply"  # Có người trả lời comment
    UPVOTE_RECEIVED = "upvote_received"  # Nhận upvote
    INCIDENT_NEARBY = "incident_nearby"  # Sự kiện gần vị trí user
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"  # Mở khóa thành tựu
    LEVEL_UP = "level_up"  # Tăng level
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # Thông báo hệ thống
    DEPARTMENT_MESSAGE = "department_message"  # Tin nhắn từ cơ quan quản lý


class NotificationChannel(str, enum.Enum):
    """Kênh gửi thông báo"""
    IN_APP = "in_app"  # Trong app
    PUSH = "push"  # Push notification (FCM/APNs)
    EMAIL = "email"  # Email
    SMS = "sms"  # SMS (optional)


class Notification(Base):
    """Bảng thông báo"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Additional data (flexible JSONB for different notification types)
    data = Column(JSONB)
    # Example data structures:
    # - report_status_change: {"report_id": 123, "old_status": "pending", "new_status": "verified"}
    # - report_comment: {"report_id": 123, "comment_id": 456, "commenter_name": "John"}
    # - incident_nearby: {"incident_id": 789, "distance_km": 2.5, "incident_type": "flood"}
    
    # Action URL (deep link for mobile/web)
    action_url = Column(String(500))
    
    # Read status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True))
    
    # Delivery status per channel
    sent_in_app = Column(Boolean, default=True)  # Always true for in-app
    sent_push = Column(Boolean, default=False)
    sent_email = Column(Boolean, default=False)
    sent_sms = Column(Boolean, default=False)
    
    # Delivery timestamps
    sent_push_at = Column(DateTime(timezone=True))
    sent_email_at = Column(DateTime(timezone=True))
    sent_sms_at = Column(DateTime(timezone=True))
    
    # Delivery errors
    push_error = Column(Text)
    email_error = Column(Text)
    sms_error = Column(Text)
    
    # Priority (for sorting and UI emphasis)
    priority = Column(Integer, default=1)  # 1=normal, 2=high, 3=urgent
    
    # Expiry (for time-sensitive notifications)
    expires_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserNotificationSettings(Base):
    """Cài đặt thông báo của người dùng"""
    __tablename__ = "user_notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Global toggles
    enabled_in_app = Column(Boolean, default=True)
    enabled_push = Column(Boolean, default=True)
    enabled_email = Column(Boolean, default=True)
    enabled_sms = Column(Boolean, default=False)
    
    # Per-type settings (JSONB for flexibility)
    # Structure: {"report_status_change": {"in_app": true, "push": true, "email": false}}
    type_settings = Column(JSONB, default={})
    
    # Quiet hours (do not disturb)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))  # "08:00"
    
    # Device tokens for push notifications
    fcm_tokens = Column(JSONB, default=[])  # Firebase Cloud Messaging tokens (Android)
    apns_tokens = Column(JSONB, default=[])  # Apple Push Notification Service tokens (iOS)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationTemplate(Base):
    """Template cho thông báo (dễ dàng i18n và customize)"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False, unique=True, index=True)
    
    # Templates với placeholder variables: {variable_name}
    title_template = Column(String(255), nullable=False)
    # Example: "Báo cáo #{report_id} đã được {status}"
    
    message_template = Column(Text, nullable=False)
    # Example: "Báo cáo '{report_title}' của bạn đã được chuyển sang trạng thái {status}. Xem chi tiết tại đây."
    
    # Email template (optional)
    email_subject_template = Column(String(255))
    email_body_template = Column(Text)
    
    # Action button text
    action_button_text = Column(String(100))  # "Xem báo cáo", "Xem chi tiết", etc.
    
    # Icon/emoji for rich notifications
    icon = Column(String(100))
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
