# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Assignment endpoints - Phân công và quản lý báo cáo
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.services.assignment_service import AssignmentService
from app.models.assignment import Department, ReportAssignment, AssignmentStatus
from app.models.user import User
from app.models.report import Report
from app.schemas.assignment import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentListResponse,
    AssignmentAccept,
    AssignmentReject,
    AssignmentComplete,
    AssignmentNote,
    DepartmentStatsResponse
)

router = APIRouter()


# ============================================
# DEPARTMENT ENDPOINTS
# ============================================

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_in: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo department mới (Admin only)
    
    - **code**: Mã department (unique)
    - **name_vi**: Tên tiếng Việt
    - **name_en**: Tên tiếng Anh
    - **categories**: Danh sách category codes phụ trách
    - **districts**: Danh sách district IDs (optional)
    - **sla_response_hours**: Thời hạn phản hồi (mặc định 24h)
    - **sla_resolution_hours**: Thời hạn giải quyết (mặc định 72h)
    """
    # Check unique code
    existing = db.query(Department).filter(Department.code == department_in.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with code '{department_in.code}' already exists"
        )
    
    department = Department(**department_in.dict())
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return department


@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách departments
    
    - **is_active**: Lọc theo trạng thái active
    - **category**: Lọc theo category phụ trách
    """
    query = db.query(Department)
    
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    if category:
        query = query.filter(Department.categories.contains([category]))
    
    departments = query.order_by(Department.name_vi).offset(skip).limit(limit).all()
    
    return departments


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Lấy thông tin chi tiết department"""
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return department


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int = Path(..., description="Department ID"),
    department_update: DepartmentUpdate = ...,
    db: Session = Depends(get_db)
):
    """Cập nhật department (Admin only)"""
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update fields
    for key, value in department_update.dict(exclude_unset=True).items():
        setattr(department, key, value)
    
    db.commit()
    db.refresh(department)
    
    return department


@router.get("/departments/{department_id}/stats", response_model=DepartmentStatsResponse)
async def get_department_stats(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Thống kê performance của department"""
    service = AssignmentService(db)
    
    try:
        stats = service.get_department_stats(department_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# ASSIGNMENT ENDPOINTS
# ============================================

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_in: AssignmentCreate,
    user_id: int = Query(..., description="User ID (assigned_by)"),
    db: Session = Depends(get_db)
):
    """
    Tạo phân công mới
    
    - **report_id**: ID báo cáo
    - **department_id**: ID department
    - **assigned_to**: ID cá nhân (optional)
    - **priority**: 1=urgent, 2=high, 3=normal, 4=low
    - **notes**: Ghi chú
    """
    # Check report exists
    report = db.query(Report).filter(Report.id == assignment_in.report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check department exists
    department = db.query(Department).filter(Department.id == assignment_in.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    service = AssignmentService(db)
    
    try:
        assignment = service.create_assignment(
            report_id=assignment_in.report_id,
            department_id=assignment_in.department_id,
            assigned_by=user_id,
            assigned_to=assignment_in.assigned_to,
            priority=assignment_in.priority,
            notes=assignment_in.notes
        )
        
        # Enrich response
        assignment.department_name = department.name_vi
        assignment.report_title = report.title
        
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reports/{report_id}/auto-assign")
async def auto_assign_report(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID (system)"),
    db: Session = Depends(get_db)
):
    """
    Tự động phân công báo cáo dựa trên category và location
    
    Hệ thống sẽ tìm department phù hợp nhất
    """
    service = AssignmentService(db)
    assignment = service.auto_assign_report(report_id, user_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No suitable department found for this report"
        )
    
    return {
        "status": "success",
        "assignment_id": assignment.id,
        "department_id": assignment.department_id
    }


@router.post("/assignments/{assignment_id}/accept", response_model=AssignmentResponse)
async def accept_assignment(
    assignment_id: int = Path(..., description="Assignment ID"),
    accept_data: AssignmentAccept = ...,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Department tiếp nhận phân công
    
    - **estimated_completion**: Thời gian dự kiến hoàn thành
    - **notes**: Ghi chú
    """
    service = AssignmentService(db)
    
    try:
        assignment = service.accept_assignment(
            assignment_id=assignment_id,
            user_id=user_id,
            estimated_completion=accept_data.estimated_completion,
            notes=accept_data.notes
        )
        
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assignments/{assignment_id}/reject", response_model=AssignmentResponse)
async def reject_assignment(
    assignment_id: int = Path(..., description="Assignment ID"),
    reject_data: AssignmentReject = ...,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Department từ chối phân công
    
    - **rejection_reason**: Lý do từ chối (bắt buộc, min 10 ký tự)
    """
    service = AssignmentService(db)
    
    try:
        assignment = service.reject_assignment(
            assignment_id=assignment_id,
            user_id=user_id,
            rejection_reason=reject_data.rejection_reason
        )
        
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assignments/{assignment_id}/complete", response_model=AssignmentResponse)
async def complete_assignment(
    assignment_id: int = Path(..., description="Assignment ID"),
    complete_data: AssignmentComplete = ...,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Hoàn thành phân công
    
    - **resolution_note**: Báo cáo kết quả (bắt buộc, min 10 ký tự)
    - **resolution_attachments**: Danh sách URL file đính kèm
    """
    service = AssignmentService(db)
    
    try:
        assignment = service.complete_assignment(
            assignment_id=assignment_id,
            user_id=user_id,
            resolution_note=complete_data.resolution_note,
            resolution_attachments=complete_data.resolution_attachments
        )
        
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assignments/{assignment_id}/notes")
async def add_assignment_note(
    assignment_id: int = Path(..., description="Assignment ID"),
    note_data: AssignmentNote = ...,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Thêm ghi chú vào assignment
    
    - **note**: Nội dung ghi chú
    - **note_type**: update, issue, solution, escalation
    """
    service = AssignmentService(db)
    
    try:
        assignment = service.add_note(
            assignment_id=assignment_id,
            user_id=user_id,
            note=note_data.note,
            note_type=note_data.note_type
        )
        
        return {
            "status": "success",
            "note_added": True,
            "total_notes": len(assignment.notes or [])
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int = Path(..., description="Assignment ID"),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết assignment"""
    assignment = db.query(ReportAssignment).filter(
        ReportAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Enrich with related data
    department = db.query(Department).filter(Department.id == assignment.department_id).first()
    report = db.query(Report).filter(Report.id == assignment.report_id).first()
    
    if department:
        assignment.department_name = department.name_vi
    if report:
        assignment.report_title = report.title
    if assignment.assigned_to:
        user = db.query(User).filter(User.id == assignment.assigned_to).first()
        if user:
            assignment.assigned_to_name = user.full_name or user.username
    
    return assignment


@router.get("/departments/{department_id}/assignments", response_model=AssignmentListResponse)
async def get_department_assignments(
    department_id: int = Path(..., description="Department ID"),
    status: Optional[AssignmentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách phân công của department
    
    - **status**: Lọc theo trạng thái (assigned, accepted, working, completed, rejected)
    - **skip, limit**: Phân trang
    """
    service = AssignmentService(db)
    assignments, total = service.get_department_assignments(
        department_id=department_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return {
        "assignments": assignments,
        "total": total
    }


@router.get("/my-assignments", response_model=AssignmentListResponse)
async def get_my_assignments(
    user_id: int = Query(..., description="User ID"),
    status: Optional[AssignmentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách phân công của user (government staff)
    
    - **status**: Lọc theo trạng thái
    - **skip, limit**: Phân trang
    """
    service = AssignmentService(db)
    assignments, total = service.get_user_assignments(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return {
        "assignments": assignments,
        "total": total
    }


@router.post("/assignments/check-overdue")
async def check_overdue_assignments(
    db: Session = Depends(get_db)
):
    """
    Kiểm tra và đánh dấu assignments quá hạn
    
    Endpoint này nên được gọi định kỳ (cron job)
    """
    service = AssignmentService(db)
    count = service.check_overdue_assignments()
    
    return {
        "status": "success",
        "overdue_count": count
    }
