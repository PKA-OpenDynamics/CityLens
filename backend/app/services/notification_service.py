# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Notification Service - Business logic cho thông báo

Service này xử lý:
- Tạo và gửi thông báo
- Quản lý device tokens
- Gửi qua nhiều kênh (in-app, push, email)
- Áp dụng user preferences
- Template rendering
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, time as dt_time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.notification import (
    Notification, 
    UserNotificationSettings, 
    NotificationTemplate,
    NotificationType,
    NotificationChannel
)
from app.models.user import User


class NotificationService:
    """Service xử lý business logic cho notification"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        priority: int = 1,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Notification:
        """
        Tạo và gửi thông báo
        
        Args:
            user_id: ID người nhận
            notification_type: Loại thông báo
            title: Tiêu đề
            message: Nội dung
            data: Dữ liệu bổ sung (JSONB)
            action_url: Deep link
            priority: Mức độ ưu tiên (1=normal, 2=high, 3=urgent)
            channels: Kênh gửi (mặc định: in-app)
        
        Returns:
            Notification object đã tạo
        """
        # Get user notification settings
        settings = self._get_user_settings(user_id)
        
        # Determine which channels to use
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        # Check user preferences
        enabled_channels = self._filter_enabled_channels(
            channels, 
            settings, 
            notification_type
        )
        
        # Check quiet hours
        if settings and self._is_quiet_hours(settings):
            # Only in-app during quiet hours
            enabled_channels = [ch for ch in enabled_channels if ch == NotificationChannel.IN_APP]
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
            action_url=action_url,
            priority=priority,
            sent_in_app=True  # Always created in-app
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send to external channels asynchronously
        for channel in enabled_channels:
            if channel == NotificationChannel.PUSH:
                await self._send_push_notification(notification, settings)
            elif channel == NotificationChannel.EMAIL:
                await self._send_email_notification(notification, settings)
            elif channel == NotificationChannel.SMS:
                await self._send_sms_notification(notification, settings)
        
        return notification
    
    async def create_bulk_notifications(
        self,
        user_ids: List[int],
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        priority: int = 1
    ) -> int:
        """
        Tạo thông báo hàng loạt cho nhiều người dùng
        
        Args:
            user_ids: Danh sách user IDs
            notification_type: Loại thông báo
            title: Tiêu đề
            message: Nội dung
            data: Dữ liệu bổ sung
            action_url: Deep link
            priority: Mức độ ưu tiên
        
        Returns:
            Số lượng notifications đã tạo
        """
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data,
                action_url=action_url,
                priority=priority,
                sent_in_app=True
            )
            notifications.append(notification)
        
        self.db.bulk_save_objects(notifications)
        self.db.commit()
        
        # TODO: Send push/email for bulk notifications asynchronously
        
        return len(notifications)
    
    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> tuple[List[Notification], int]:
        """
        Lấy danh sách thông báo của user
        
        Args:
            user_id: ID người dùng
            skip: Số lượng bỏ qua (pagination)
            limit: Số lượng tối đa
            unread_only: Chỉ lấy chưa đọc
        
        Returns:
            Tuple (notifications, total_count)
        """
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        total = query.count()
        
        notifications = query.order_by(
            Notification.priority.desc(),
            Notification.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return notifications, total
    
    def get_unread_count(self, user_id: int) -> int:
        """Đếm số thông báo chưa đọc"""
        return self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()
    
    def mark_as_read(self, notification_ids: List[int], user_id: int) -> int:
        """
        Đánh dấu thông báo đã đọc
        
        Args:
            notification_ids: Danh sách notification IDs
            user_id: ID người dùng (để verify ownership)
        
        Returns:
            Số lượng notifications đã mark
        """
        count = self.db.query(Notification).filter(
            and_(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        return count
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Đánh dấu tất cả thông báo đã đọc"""
        count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Xóa thông báo"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def get_user_settings(self, user_id: int) -> Optional[UserNotificationSettings]:
        """Lấy settings thông báo của user"""
        return self._get_user_settings(user_id)
    
    def update_user_settings(
        self,
        user_id: int,
        settings_data: Dict[str, Any]
    ) -> UserNotificationSettings:
        """Cập nhật settings thông báo"""
        settings = self._get_user_settings(user_id)
        
        if not settings:
            settings = UserNotificationSettings(user_id=user_id)
            self.db.add(settings)
        
        # Update fields
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def register_device_token(
        self,
        user_id: int,
        token: str,
        platform: str
    ) -> bool:
        """
        Đăng ký device token cho push notifications
        
        Args:
            user_id: ID người dùng
            token: FCM/APNs token
            platform: "android" or "ios"
        
        Returns:
            True nếu thành công
        """
        settings = self._get_user_settings(user_id)
        
        if not settings:
            settings = UserNotificationSettings(user_id=user_id)
            self.db.add(settings)
        
        if platform == "android":
            tokens = settings.fcm_tokens or []
            if token not in tokens:
                tokens.append(token)
                settings.fcm_tokens = tokens
        elif platform == "ios":
            tokens = settings.apns_tokens or []
            if token not in tokens:
                tokens.append(token)
                settings.apns_tokens = tokens
        
        self.db.commit()
        return True
    
    def unregister_device_token(
        self,
        user_id: int,
        token: str,
        platform: str
    ) -> bool:
        """Gỡ bỏ device token"""
        settings = self._get_user_settings(user_id)
        
        if not settings:
            return False
        
        if platform == "android" and settings.fcm_tokens:
            tokens = [t for t in settings.fcm_tokens if t != token]
            settings.fcm_tokens = tokens
        elif platform == "ios" and settings.apns_tokens:
            tokens = [t for t in settings.apns_tokens if t != token]
            settings.apns_tokens = tokens
        
        self.db.commit()
        return True
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Thống kê thông báo của user"""
        total = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).count()
        
        unread = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()
        
        # Count by type
        by_type = {}
        type_counts = self.db.query(
            Notification.type,
            func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id
        ).group_by(Notification.type).all()
        
        for notif_type, count in type_counts:
            by_type[notif_type.value] = count
        
        # Last 7 days
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        last_7_days = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.created_at >= seven_days_ago
            )
        ).count()
        
        return {
            "total": total,
            "unread": unread,
            "by_type": by_type,
            "last_7_days": last_7_days
        }
    
    # Private helper methods
    
    def _get_user_settings(self, user_id: int) -> Optional[UserNotificationSettings]:
        """Lấy settings, tạo mới nếu chưa có"""
        settings = self.db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            # Create default settings
            settings = UserNotificationSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def _filter_enabled_channels(
        self,
        channels: List[NotificationChannel],
        settings: Optional[UserNotificationSettings],
        notification_type: NotificationType
    ) -> List[NotificationChannel]:
        """Filter channels dựa trên user settings"""
        if not settings:
            return channels
        
        enabled = []
        
        for channel in channels:
            # Check global toggle
            if channel == NotificationChannel.IN_APP and not settings.enabled_in_app:
                continue
            elif channel == NotificationChannel.PUSH and not settings.enabled_push:
                continue
            elif channel == NotificationChannel.EMAIL and not settings.enabled_email:
                continue
            elif channel == NotificationChannel.SMS and not settings.enabled_sms:
                continue
            
            # Check type-specific settings
            type_settings = settings.type_settings or {}
            if notification_type.value in type_settings:
                type_prefs = type_settings[notification_type.value]
                if not type_prefs.get(channel.value, True):
                    continue
            
            enabled.append(channel)
        
        return enabled
    
    def _is_quiet_hours(self, settings: UserNotificationSettings) -> bool:
        """Kiểm tra có phải quiet hours không"""
        if not settings.quiet_hours_enabled:
            return False
        
        if not settings.quiet_hours_start or not settings.quiet_hours_end:
            return False
        
        try:
            now = datetime.utcnow().time()
            start = dt_time.fromisoformat(settings.quiet_hours_start)
            end = dt_time.fromisoformat(settings.quiet_hours_end)
            
            if start < end:
                return start <= now <= end
            else:  # Crosses midnight
                return now >= start or now <= end
        except:
            return False
    
    async def _send_push_notification(
        self,
        notification: Notification,
        settings: Optional[UserNotificationSettings]
    ):
        """Gửi push notification (FCM/APNs)"""
        # TODO: Implement Firebase Cloud Messaging integration
        # For now, just mark as sent
        notification.sent_push = True
        notification.sent_push_at = datetime.utcnow()
        self.db.commit()
    
    async def _send_email_notification(
        self,
        notification: Notification,
        settings: Optional[UserNotificationSettings]
    ):
        """Gửi email notification"""
        # TODO: Implement email sending (SMTP/SendGrid/AWS SES)
        # For now, just mark as sent
        notification.sent_email = True
        notification.sent_email_at = datetime.utcnow()
        self.db.commit()
    
    async def _send_sms_notification(
        self,
        notification: Notification,
        settings: Optional[UserNotificationSettings]
    ):
        """Gửi SMS notification"""
        # TODO: Implement SMS sending (Twilio/AWS SNS)
        # For now, just mark as sent
        notification.sent_sms = True
        notification.sent_sms_at = datetime.utcnow()
        self.db.commit()


# Convenience functions for common notification scenarios

async def notify_report_status_change(
    db: Session,
    user_id: int,
    report_id: int,
    report_title: str,
    old_status: str,
    new_status: str
):
    """Thông báo khi báo cáo thay đổi trạng thái"""
    service = NotificationService(db)
    
    status_map = {
        "pending": "chờ xác minh",
        "verified": "đã xác minh",
        "in_progress": "đang xử lý",
        "resolved": "đã giải quyết",
        "rejected": "bị từ chối"
    }
    
    await service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.REPORT_STATUS_CHANGE,
        title=f"Báo cáo #{report_id} đã cập nhật",
        message=f"Báo cáo '{report_title}' đã chuyển sang trạng thái {status_map.get(new_status, new_status)}",
        data={
            "report_id": report_id,
            "old_status": old_status,
            "new_status": new_status
        },
        action_url=f"/reports/{report_id}",
        priority=2,
        channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH]
    )


async def notify_new_comment(
    db: Session,
    user_id: int,
    report_id: int,
    report_title: str,
    commenter_name: str,
    comment_id: int
):
    """Thông báo khi có comment mới"""
    service = NotificationService(db)
    
    await service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.REPORT_COMMENT,
        title="Có bình luận mới",
        message=f"{commenter_name} đã bình luận trên báo cáo '{report_title}'",
        data={
            "report_id": report_id,
            "comment_id": comment_id,
            "commenter_name": commenter_name
        },
        action_url=f"/reports/{report_id}#comment-{comment_id}",
        priority=1,
        channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH]
    )


async def notify_report_assigned(
    db: Session,
    user_id: int,
    report_id: int,
    report_title: str,
    department_name: str
):
    """Thông báo khi báo cáo được phân công"""
    service = NotificationService(db)
    
    await service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.REPORT_ASSIGNED,
        title="Báo cáo được tiếp nhận",
        message=f"Báo cáo '{report_title}' đã được chuyển đến {department_name}",
        data={
            "report_id": report_id,
            "department_name": department_name
        },
        action_url=f"/reports/{report_id}",
        priority=2,
        channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH, NotificationChannel.EMAIL]
    )
