# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Notification models - Thông báo cho người dùng
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import enum
import uuid
from app.db.postgres import Base


class NotificationType(str, enum.Enum):
    """Loại thông báo"""
    REPORT_STATUS_UPDATE = "report_status_update"
    REPORT_COMMENT = "report_comment"
    REPORT_UPVOTE = "report_upvote"
    REPORT_ASSIGNED = "report_assigned"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"


class NotificationChannel(str, enum.Enum):
    """Kênh gửi thông báo"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class Notification(Base):
    """Thông báo"""
    __tablename__ = "notifications"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related objects
    related_report_id = Column(PGUUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    related_user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Additional data
    data = Column(JSONB, comment="Extra notification data")
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Notification {self.type} for user {self.user_id}>"


class UserNotificationSettings(Base):
    """Cài đặt thông báo của người dùng"""
    __tablename__ = "user_notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Enable/disable channels
    enable_email = Column(Boolean, default=True)
    enable_push = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)
    
    # Enable/disable notification types
    notify_status_update = Column(Boolean, default=True)
    notify_comments = Column(Boolean, default=True)
    notify_upvotes = Column(Boolean, default=True)
    notify_assignments = Column(Boolean, default=True)
    notify_announcements = Column(Boolean, default=True)
    
    # Quiet hours
    quiet_hours_start = Column(String(5), comment="HH:MM format")
    quiet_hours_end = Column(String(5), comment="HH:MM format")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationSettings user={self.user_id}>"


class NotificationTemplate(Base):
    """Template cho các loại thông báo"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False, unique=True, index=True)
    
    # Template content
    title_template = Column(String(255), nullable=False, comment="e.g. 'Báo cáo #{report_id} đã {status}'")
    message_template = Column(Text, nullable=False)
    
    # Email template (optional)
    email_subject_template = Column(String(255))
    email_body_template = Column(Text)
    
    # Push notification
    push_title_template = Column(String(255))
    push_body_template = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate {self.type}>"
