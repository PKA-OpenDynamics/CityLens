# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Assignment models - Phân công xử lý báo cáo
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import enum
import uuid
from app.db.postgres import Base


class AssignmentStatus(str, enum.Enum):
    """Trạng thái phân công"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Department(Base):
    """Phòng ban chịu trách nhiệm"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    email = Column(String(255))
    phone = Column(String(50))
    
    # Categories this department handles
    responsible_categories = Column(JSONB, comment="List of category codes")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Department {self.name}>"


class DepartmentMember(Base):
    """Thành viên của phòng ban"""
    __tablename__ = "department_members"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Role in department
    role = Column(String(50), default="member", comment="manager, member, viewer")
    
    # Status
    is_active = Column(Boolean, default=True)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DepartmentMember user={self.user_id} dept={self.department_id}>"


class ReportAssignment(Base):
    """Phân công xử lý báo cáo"""
    __tablename__ = "report_assignments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    
    # Assigned by & to
    assigned_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, 
                         comment="Specific user in department")
    
    # Status
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.PENDING, nullable=False, index=True)
    
    # Notes
    assignment_note = Column(Text)
    completion_note = Column(Text)
    
    # Timestamps
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    accepted_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Deadline
    due_date = Column(DateTime(timezone=True), index=True)
    
    def __repr__(self):
        return f"<Assignment {self.report_id} -> Dept {self.department_id}>"


class AssignmentHistory(Base):
    """Lịch sử thay đổi assignment"""
    __tablename__ = "assignment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(PGUUID(as_uuid=True), ForeignKey("report_assignments.id"), nullable=False, index=True)
    
    # Who made the change
    changed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # What changed
    old_status = Column(Enum(AssignmentStatus))
    new_status = Column(Enum(AssignmentStatus))
    note = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<AssignmentHistory {self.old_status} -> {self.new_status}>"
