# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Assignment schemas
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.assignment import AssignmentStatus


class DepartmentBase(BaseModel):
    """Schema cơ bản cho Department"""
    code: str = Field(..., min_length=1, max_length=50)
    name_vi: str = Field(..., min_length=1, max_length=255)
    name_en: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    categories: List[str] = []
    districts: List[int] = []
    sla_response_hours: int = 24
    sla_resolution_hours: int = 72
    priority: int = Field(default=5, ge=1, le=10)


class DepartmentCreate(DepartmentBase):
    """Schema tạo Department"""
    pass


class DepartmentUpdate(BaseModel):
    """Schema cập nhật Department"""
    name_vi: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    categories: Optional[List[str]] = None
    districts: Optional[List[int]] = None
    sla_response_hours: Optional[int] = None
    sla_resolution_hours: Optional[int] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Schema trả về Department"""
    id: int
    avg_response_time_hours: float
    avg_resolution_time_hours: float
    resolution_rate: float
    total_assigned: int
    total_resolved: int
    is_active: bool
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssignmentBase(BaseModel):
    """Schema cơ bản cho Assignment"""
    notes: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=4)


class AssignmentCreate(AssignmentBase):
    """Schema tạo Assignment"""
    report_id: int
    department_id: int
    assigned_to: Optional[int] = None  # Specific person


class AssignmentUpdate(BaseModel):
    """Schema cập nhật Assignment"""
    status: Optional[AssignmentStatus] = None
    assigned_to: Optional[int] = None
    priority: Optional[int] = None
    estimated_completion: Optional[datetime] = None
    notes: Optional[str] = None


class AssignmentAccept(BaseModel):
    """Schema accept assignment"""
    estimated_completion: Optional[datetime] = None
    notes: Optional[str] = None


class AssignmentReject(BaseModel):
    """Schema reject assignment"""
    rejection_reason: str = Field(..., min_length=10, max_length=500)


class AssignmentComplete(BaseModel):
    """Schema complete assignment"""
    resolution_note: str = Field(..., min_length=10, max_length=2000)
    resolution_attachments: Optional[List[str]] = []


class AssignmentResponse(BaseModel):
    """Schema trả về Assignment"""
    id: int
    report_id: int
    department_id: int
    assigned_to: Optional[int] = None
    assigned_by: int
    assigned_at: datetime
    status: AssignmentStatus
    due_date: datetime
    response_deadline: Optional[datetime] = None
    is_overdue: bool
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    response_time_hours: Optional[float] = None
    resolution_time_hours: Optional[float] = None
    priority: int
    
    # Related data (optional)
    department_name: Optional[str] = None
    report_title: Optional[str] = None
    assigned_to_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    """Schema cho danh sách Assignments"""
    assignments: List[AssignmentResponse]
    total: int


class DepartmentStatsResponse(BaseModel):
    """Schema thống kê Department"""
    department_id: int
    department_name: str
    total_assigned: int
    total_completed: int
    total_pending: int
    total_overdue: int
    avg_response_time_hours: float
    avg_resolution_time_hours: float
    resolution_rate: float
    sla_compliance_rate: float


class AssignmentNote(BaseModel):
    """Schema thêm note vào assignment"""
    note: str = Field(..., min_length=1, max_length=500)
    note_type: str = Field(default="update", pattern="^(update|issue|solution|escalation)$")
