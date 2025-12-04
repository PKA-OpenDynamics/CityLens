# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Assignment models - Phân công báo cáo cho cơ quan chức năng
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum
from app.db.postgres import Base


class AssignmentStatus(str, enum.Enum):
    """Trạng thái phân công"""
    ASSIGNED = "assigned"  # Đã phân công
    ACCEPTED = "accepted"  # Đã tiếp nhận
    WORKING = "working"  # Đang xử lý
    COMPLETED = "completed"  # Hoàn thành
    REJECTED = "rejected"  # Từ chối


class Department(Base):
    """Cơ quan/đơn vị chức năng quản lý đô thị"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    code = Column(String(50), unique=True, nullable=False, index=True)
    name_vi = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Contact
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(String(500))
    website = Column(String(255))
    
    # Responsible for categories
    # Danh sách category codes mà department này phụ trách
    categories = Column(ARRAY(String), default=[])
    # Example: ["infrastructure_road", "infrastructure_bridge", "infrastructure_sidewalk"]
    
    # Responsible for districts
    # Danh sách district IDs (nếu department phụ trách theo khu vực)
    districts = Column(ARRAY(Integer), default=[])
    # Example: [1, 2, 3] for district IDs
    
    # Performance metrics
    avg_response_time_hours = Column(Float, default=0.0)  # Thời gian phản hồi trung bình
    avg_resolution_time_hours = Column(Float, default=0.0)  # Thời gian giải quyết TB
    resolution_rate = Column(Float, default=0.0)  # Tỷ lệ giải quyết (0.0 - 1.0)
    total_assigned = Column(Integer, default=0)  # Tổng số báo cáo được giao
    total_resolved = Column(Integer, default=0)  # Tổng số đã giải quyết
    
    # SLA (Service Level Agreement)
    sla_response_hours = Column(Integer, default=24)  # Thời hạn phản hồi (giờ)
    sla_resolution_hours = Column(Integer, default=72)  # Thời hạn giải quyết (giờ)
    
    # Priority level (for auto-assignment)
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Parent department (for hierarchy)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    # Metadata
    properties = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ReportAssignment(Base):
    """Phân công báo cáo cho cơ quan/cá nhân"""
    __tablename__ = "report_assignments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    
    # Assigned to specific person (optional)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Who created the assignment
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status workflow
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False, index=True)
    
    # SLA tracking
    due_date = Column(DateTime(timezone=True), nullable=False)  # Deadline
    response_deadline = Column(DateTime(timezone=True))  # Thời hạn phản hồi
    is_overdue = Column(Boolean, default=False, index=True)
    
    # Response from department
    accepted_at = Column(DateTime(timezone=True))
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text)
    
    # Work tracking
    started_at = Column(DateTime(timezone=True))
    estimated_completion = Column(DateTime(timezone=True))
    
    # Completion
    completed_at = Column(DateTime(timezone=True))
    resolution_note = Column(Text)
    resolution_attachments = Column(ARRAY(String), default=[])  # URLs
    
    # Time metrics (calculated)
    response_time_hours = Column(Float)  # Time from assigned to accepted
    resolution_time_hours = Column(Float)  # Time from assigned to completed
    
    # Priority (can override report priority)
    priority = Column(Integer, default=3)  # 1=urgent, 2=high, 3=normal, 4=low
    
    # Notes and updates
    notes = Column(JSONB, default=[])
    # Structure: [{"timestamp": "...", "user_id": 1, "note": "...", "type": "update"}]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AssignmentHistory(Base):
    """Lịch sử thay đổi phân công (audit trail)"""
    __tablename__ = "assignment_history"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("report_assignments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, accepted, rejected, updated, completed
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DepartmentMember(Base):
    """Thành viên của department (government users)"""
    __tablename__ = "department_members"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role within department
    role = Column(String(50), default="member")  # head, deputy, member
    
    # Permissions
    can_accept_assignments = Column(Boolean, default=True)
    can_reassign = Column(Boolean, default=False)
    can_manage_members = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
